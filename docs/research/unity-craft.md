# Unity craft

How Unity 6 projects that look striking stay fast, what Unity itself advises for URP on Apple silicon, and where our project (`unity/`, URP 17.6 on 6000.6) stands against both. Every finding is marked **keep**, **change** or **measure** against what the project does today, with the file and line. Nothing here changes the picture or the frame time on its own: each change that would goes to the frame-rate gate and is A/B'd on the harness first (`docs/measuring.md`). The raw evidence is in `reviews/unity-craft/` (`notes-games.md`, `notes-official.md`, `notes-cities-apple.md`). This study does not repeat `performance-craft.md`, whose eight items stand; it adds the settings, shaders, builds and code around them.

## In short

1. **The project's rendering skeleton is right.** Forward+, the SRP Batcher, Render Graph raster passes in our own feature, no static or dynamic batching, linear HDR at 32 bits. Keep.
2. **The architecture's shaders are not built yet.** No shader declares `DOTS_INSTANCING_ON`, `LOD_FADE_CROSSFADE` or `unity_RendererUserValue`, and the three surface shaders target 3.5. The GPU Resident Drawer is off and BatchRendererGroup variants are not kept. That fits turning the Drawer on at step 3.4; the rules say so, and a shader template carries the pragmas so new shaders are born ready.
3. **URP's LOD cross-fade is on, but no shader implements it,** and the PC quality level doubles every switch distance (`lodBias` 2). Both bite the moment levels land; fix them with the levels.
4. **Harness and look-test switches are compiled into every game build.** Stone's forward pass multiplies URP's own keyword set by 160. On Metal each variant met for the first time is a pipeline compile, a hitch the timings count as frame time. Strip them from game builds, log the variant count, and warm the rest from a traced collection.
5. **On a tile GPU the costs are bandwidth and passes.** Our three full-screen features each copy the frame; something after the opaques stores MSAA's samples; the opaque texture is kept though nothing of ours reads it. These go with `performance-craft.md` item 5, measured.
6. **Timing builds run Mono with no warm-up and default frame pacing.** IL2CPP (waiting on Øystein's permission), a traced shader warm-up and MetalDisplayLink are each a measured change, not a switch.
7. **Unity's checks become ours.** A Unity settings and code audit joins `tools/check.py`: the settings below as expected values with reasons, the shader rules, the code rules, and the build's variant count.

## What the sources agree on

**Light, fog and grade carry the look; materials stay cheap.** Firewatch's grey rocks lit by fog and grade, Sable's fog "had the biggest impact overall", INSIDE refused SSAO for hand-aimed decals, Genshin rejected ACES because it didn't fit its style (`notes-games.md`). Our one shade function, one stage and palette grade are this rule. Keep.

**Narrow tricks beat general features, and cost is spread over time and pixels.** Interleaved shadow cascades (Genshin), shadow maps spread over frames (INSIDE), quarter-size beams, render scale below output (Valheim, A Short Hike). `performance-craft.md` already ranks these for us. Keep its order.

**Instancing doesn't save geometry.** Cities: Skylines II drew everything through its own BatchRendererGroup and still spent its frame on vertices: missing levels, no occlusion culling, shadows about half the frame (Huhtala's analysis, read through press summaries; the makers confirmed the missing levels). Our design makes levels and caster proxies in the generator. Keep, and treat the Resident Drawer as a CPU tool, not a GPU one.

**A procedural world culls from its own structure.** Shadows of Doubt uses its generated doors as culling portals and its tile grid for culling, because nothing can be baked. Townscaper's colours multiplied its kit, so state is better carried in shader inputs than in new pieces. Both fit our records and history maps. Keep; the generator's openings are a culling input to test when interiors arrive.

**On Apple silicon, every byte leaving the tile costs.** Hidden surfaces are removed before shading for opaque fragments, so depth prepasses are "usually unnecessary"; alpha-tested and blended fragments break that; load and store actions run per tile, MSAA can resolve in tile memory, and fewer passes means fewer loads and stores (Apple, WWDC20 10602 and 10632). Unity's render graph merges raster passes into native render passes on Metal, reads the same pixel by framebuffer fetch, and cannot merge unsafe or compute passes. Its XR guidance for tile GPUs: drop the opaque and depth textures unless needed, no depth priming.

**The Resident Drawer has hard entry rules and a GPU price.** It needs Forward+, the SRP Batcher, BatchRendererGroup variants kept ("Keep All"), Mesh Renderers and DOTS-instanced shaders; it excludes objects with a MaterialPropertyBlock, realtime GI or per-object callbacks. It lowers CPU cost and "slightly increases GPU workload… if your application is GPU-bound, overall frame time might increase". Its occlusion culling tests bounding spheres. Our frame is GPU-bound with about 1 ms of main thread.

**Metal compiles per pipeline state.** Unity 6's `GraphicsStateCollection` traces the states a development build meets and warms them while loading; Unity says its older shader warm-up is not fully supported on Metal. Apple's Metal HUD flags compiles during play as hitches.

**Time players, not the editor.** IL2CPP needs Xcode and is Unity's faster backend; Apple silicon is the recommended macOS target. Unity's "Metal API Validation" checks bindings in the editor only and is not Apple's validation, which needs a Debug run from Xcode. Frame Timing Stats must be on for `FrameTimingManager`.

## The project against the craft

Each row: the mark, the rule, where, how much it matters, and the fix. Paths are under `unity/`.

### The pipeline and its passes

| # | Mark | Rule | Where | Matters | Fix |
| --- | --- | --- | --- | --- | --- |
| U1 | keep | Forward+ is the path the Drawer needs; lights beyond its 256 come from tiers | `Assets/Settings/PC_Renderer.asset:95` | high | none; the lamp tiers stay in `building-blocks.md` |
| U2 | keep | SRP Batcher on; static and dynamic batching off (the Drawer wants static batching off) | `PC_RPAsset.asset:72-73`; `ProjectSettings/ProjectSettings.asset:474` | high | none |
| U3 | keep | Custom passes are render-graph raster passes, skipped when idle | `Assets/Code/Scenes/SunBeamsFeature.cs:197-279` (the one unsafe pass, `:238`, is a harness arm) | high | it becomes the render-pass template |
| U4 | measure | No copies: read the frame by framebuffer fetch | three `FullScreenPassRendererFeature`s, each `fetchColorBuffer: 1`: `PC_Renderer.asset:17`, `:37` (before post), `:173` (the palette, after post) | 2.6 to 3.8 ms | fog lights and key block as one raster pass, skipped when idle; the palette into the grade's LUT if it reads no neighbours (`performance-craft.md` item 5) |
| U5 | measure | Keep MSAA samples on tile | `PC_Renderer.asset:97` sets depth After Opaques, but SSAO's DepthNormals prepass (`:134`) most likely supplies the depth texture, so no copy runs; the colour readers after opaques (SSR, `:116`; U4's features) are the likelier cause of MSAA's store | MSAA's 1.8 ms on an empty frame | the Render Graph Viewer and an Xcode capture name the stores before any setting changes; `m_StoreActionsOptimization` stays Auto (`PC_RPAsset.asset:77`) |
| U6 | measure | No opaque texture unless an effect reads it | `PC_RPAsset.asset:23-24`; no shader of ours samples `_CameraOpaqueTexture` | under the harness's noise, but a full copy | confirm URP's SSR doesn't read it, then off |
| U7 | measure | SSAO at the size it reads at, from depth | `PC_Renderer.asset:132` (`Downsample: 0`), `:134` (`Source: 1`, DepthNormals) | 2.4 to 4.3 ms | `performance-craft.md` item 6 |
| U8 | keep | No temporal accumulation; MSAA until 3.4, then the filter chosen on levelled geometry | `PC_RPAsset.asset:28` | high | as designed; STP stays out (it forces TAA and excludes dynamic resolution) |
| U9 | measure | Depth priming only where it pays | `PC_Renderer.asset:96` (Disabled) | the architecture's 0.5 ms for `OS_History` assumes priming on | A/B Forced against Disabled on the M4; Apple says the prepass buys nothing for opaque fragments, and Unity's docs don't say whether a Mac counts as a tile GPU |

### Shadows and light

| # | Mark | Rule | Where | Matters | Fix |
| --- | --- | --- | --- | --- | --- |
| U10 | measure | Fewer cascades, shorter reach, a smaller filter | `PC_RPAsset.asset:46` (4096), `:57` (200 m), `:58` (4 cascades), `:69` (soft quality High) | 7.1 ms in drizzle against a 2.0 line | three cascades, Medium, distance by camera stop; with `performance-craft.md` item 2's far shadows |
| U11 | keep | No baked probes or lightmaps for generated places | `PC_RPAsset.asset:36` (`m_LightProbeSystem: 0`: legacy probes, no probe volumes) | high | none; Adaptive Probe Volumes bake in the editor and break when geometry moves |

### Instancing, levels and culling

| # | Mark | Rule | Where | Matters | Fix |
| --- | --- | --- | --- | --- | --- |
| U12 | measure | The Drawer only where a player A/B shows it helps a GPU-bound frame | off: `PC_RPAsset.asset:85`; GPU occlusion off: `:88`; BRG variants not kept: `ProjectSettings/GraphicsSettings.asset:49` (`m_BrgStripping: 0`, not Keep All) | high, at 3.4 | at 3.4: Keep All, DOTS-instanced shaders, then the harness's Drawer and occlusion arms on the corner and the district |
| U13 | change | Shaders are born Drawer-ready | `Assets/Shaders/Stone.shader:290`, `Street.shader:50`, `Tree.shader:327` target 3.5; no shader declares `DOTS_INSTANCING_ON`, `LOD_FADE_CROSSFADE` or `unity_RendererUserValue` | high, at 3.4 | the shader template carries them; existing shaders gain them at 3.4, proved by golden views |
| U14 | change | A cross-fade the URP asset enables must exist in the shader | `PC_RPAsset.asset:33-34` (cross-fade on, blue noise) | pops instead of fades once levels land | with U13; blue noise against Bayer (Unity's optimisation advice) and Stencil (fewer variants) in the 3.4 A/B, judged on the motion sheets |
| U15 | change | Switch distances come from the pixel-error rule alone | `ProjectSettings/QualitySettings.asset:90` (`lodBias: 2` on PC) | every level twice as far as designed | 1 when levels land, or folded into each level's error |
| U16 | keep | Per-instance data never through a MaterialPropertyBlock on a renderer | the only block is the full-screen blit's, `SunBeamsFeature.cs` | high: it would exclude the renderer from the Drawer | the code check enforces it |

### Shaders, variants and pipeline states

| # | Mark | Rule | Where | Matters | Fix |
| --- | --- | --- | --- | --- | --- |
| U17 | change | Harness and look-test switches stay out of game builds | `multi_compile` for `_OS_LOOK_*`, `OS_HISTORY_OFF`, `OS_HAZE_OFF`, `OS_L5_*`: `Stone.shader:293`, `:297`, `:298`, `:306`; `Street.shader:55`, `:56`, `:58`; `Tree.shader:333-334`; `AirMotes.shader:29` | Stone's forward pass ×160 over URP's set: build time, memory, first-sight compiles | an `IPreprocessShaders` stripper keyed on the timing build's define; the harness keeps its arms. Picture unchanged; measure variants and first-sight hitches |
| U18 | change | The build reports its variant count | `PC_RPAsset.asset:144`, `UniversalRenderPipelineGlobalSettings.asset:18` (log level 0) | the check has no number to hold | log level on for check builds |
| U19 | measure | Pipeline states warmed before timing | no `GraphicsStateCollection` anywhere | first visits count as frame time | trace a Metal collection in a development build walking the corner; warm progressively behind the dated card; report first-visit hitches apart |
| U20 | keep | Every material property in one `UnityPerMaterial` block; opaque shaders carry DepthOnly, DepthNormals and ShadowCaster | `Stone.shader:39`, `Street.shader:21`, `Tree.shader:62`; passes at `Stone.shader:626-714`, `Street.shader:196-329`, `Tree.shader:647-790` | high: SRP Batcher, SSAO, priming | the check enforces it |
| U21 | change | Alpha test only where needed, depth first | `Tree.shader:441-456` and `:634` clip in the forward pass | the birch's 12.6 ms | `performance-craft.md` item 4, measured |

### Builds, timing and code

| # | Mark | Rule | Where | Matters | Fix |
| --- | --- | --- | --- | --- | --- |
| U22 | measure | Time the backend that ships | Standalone is Mono: `ProjectSettings.asset:803-804` names only Android | unknown: Unity publishes no macOS figure; it matters most for C# outside Burst | IL2CPP, Apple silicon only, after Øystein's permission (already asked) |
| U23 | keep | Frame Timing Stats on in timing builds, restored after | `Assets/Code/Editor/Measuring/LT1Perf.cs:242-266`; off in the project, `ProjectSettings.asset:160` | high | none |
| U24 | measure | Judge pacing, not only the median | `ProjectSettings.asset:122` (`metalUseMetalDisplayLink: 0`); `QualitySettings.asset:86` (`vSyncCount: 0`) | the walk felt "laggy and jumpy" | A/B MetalDisplayLink and vSync in the walk build on frame-time spread |
| U25 | keep | Unity's Metal validation stays (editor only); Apple's runs once per new render feature from an Xcode Debug build | `ProjectSettings.asset:249` | low | add the Xcode run to the render-pass template's checklist |
| U26 | keep | Nothing visible draws on `UnityEngine.Random`, `System.Random` or frame time | `Assets/Code` (`AirMotes.cs` uses the hash stream; `Time.time` only in `Walker.cs`'s fall guard) | high | the code check enforces it |
| U27 | keep | A shader found by name has a serialised reference in the build | `SkyMap.cs:54`, `:121`; references at `PlayCorner.cs:63`, `PerfRunner.cs:119` | a missing shader silently skips the sky map | the check matches each `Shader.Find` name to a reference |
| U28 | keep | No synchronous GPU readback in play | `SkyMap.cs:133` and `:148`, called only by editor checks (`LT1Heart.cs:916`); the harness syncs on purpose (`Perf/PerfRunner.cs:570`, `Perf/DistrictBench.cs:176`, `:180`) | low | the check allows it under `Editor/` and `Perf/`, and in `SkyMap`'s editor-only probes |
| U29 | change | Code compiles in assemblies, so a change rebuilds only its own | no `.asmdef` in `Assets/` (read directly in Unity's Manual, not in the notes) | iteration time | assemblies by folder (Core, World, Assembly, Scenes, Play, Perf, Editor) when code next moves |
| U30 | keep | Burst for every loop over parts or vertices in play | Burst and Collections are built-in dependencies of the render pipeline core (`Packages/packages-lock.json`, depth 2); Mathematics is not in the project; the one Burst job is the scale bench, `Assets/Code/Perf/DistrictBench.cs` | high once the assembler moves to C# | name Burst, Collections and Mathematics in `manifest.json` with the first game job |
| U31 | keep | Adaptive Performance is harmless on a Mac with no provider | `PC_RPAsset.asset:78` | none | none |

## What the design pages assume

- `building-blocks.md` (Instancing) lists the Drawer's pragmas as the shaders' and Burst, Collections and Mathematics as named in `manifest.json`; both are step 3.4 and first-job work (U13, U30). `_OS_BAKE` is reserved for 3.1 and in no shader yet.
- `building-blocks.md` plans depth priming on with SMAA, and `performance-craft.md` says Unity turns priming off on tile hardware. Unity's docs name only Android, iOS and Apple TV; on the M4 it is a measured question (U9).

## The order

Each step names what it changes; none changes the picture or the frame time unmeasured. Each measured change is decided in a line when its build reaches it, with its harness A/B.

1. **Now, no picture change.**
   - *The Unity audit in `tools/check.py`* when it lands: (a) settings: the expected values of U1, U2, U11, U12's stripping (once the Drawer is chosen), U14's dither (once chosen), U15, U18 and U23, each with its reason, read from the YAML; (b) shaders: the `UnityPerMaterial` block, the three depth and shadow passes on opaque shaders, no harness keyword as `multi_compile` outside a stripped list, the template's pragmas once 3.4 lands; (c) code: no `Random` or frame time in visible choices, no renderer `MaterialPropertyBlock`, every `Shader.Find` referenced, no synchronous readback outside `Editor/`, `Perf/` and editor-only probes; (d) the build's variant count against a ceiling. It reports, and fails only on rules already met, so it passes on the project as it stands.
   - *Templates:* a shader template (Forward+ keywords, the per-material block, the four passes, `_OS_BAKE`, the 3.4 pragmas behind one include) and a render-pass template (raster passes, framebuffer fetch for same-pixel reads, idle skip, a profiling sampler, the Render Graph Viewer and Xcode checks).
   - *U17 and U18:* strip the harness's switches from game builds and log variants. Proved by golden views bit-identical and the timing harness's arms unchanged.
2. **With the frame-rate gate, in `performance-craft.md`'s order.** Its item 3, the Xcode capture, with U19's warm-up, so every later timing excludes compiles; then item 2 with U10; item 5 with U4, U5 and U6; item 4 with U21; item 6 with U7; U9 and U24 as their own A/Bs.
3. **At 3.4, with the levels.** U12 to U15 together: the pragmas, the cross-fade, `lodBias` and the Drawer's A/B on the corner and the district, then the anti-aliasing choice (U8).
4. **Before the port's step 5.** U22, IL2CPP against Mono, once Øystein allows the module.

## Gaps

- No PDF of Unity's e-books was read; their summaries and the Manual stand in.
- Huhtala's analysis and the Megacity Metro README were not opened; their lines rest on press summaries.
- Whether URP treats an Apple silicon Mac as a tile GPU for depth priming and memoryless targets, and whether `GraphicsStateCollection` uses Metal binary archives, are undocumented: U5, U9 and U19 answer them by measurement.
- The URP 3D Sample's Garden, the nearest official precedent (a stylised modular town on Forward+), was not opened in Unity 6.

## Sources

Unity:
- [Best practice guides (6000.4)](https://docs.unity3d.com/6000.4/Documentation/Manual/best-practice-guides.html)
- [Unity 6 optimisation guides](https://unity.com/blog/unity-6-game-optimization-guides)
- [URP cookbook, Unity 6](https://unity.com/resources/create-shaders-visual-effects-urp-unity-6)
- [Forward+ limitations](https://docs.unity3d.com/Manual/urp/rendering/forward-plus-rendering-path-limitations.html)
- [GPU Resident Drawer](https://docs.unity3d.com/6000.3/Documentation/Manual/urp/gpu-resident-drawer.html)
- [Make objects compatible with GPU rendering](https://docs.unity3d.com/Manual/urp/make-object-compatible-gpu-rendering.html)
- [GPU Resident Drawer performance](https://docs.unity3d.com/Manual/urp/gpu-resident-drawer-performance.html)
- [GPU occlusion culling](https://docs.unity3d.com/6000.2/Documentation/Manual/urp/gpu-culling.html)
- [Optimise a render graph](https://docs.unity3d.com/kr/6000.0/Manual/urp/render-graph-optimize.html)
- [Framebuffer fetch in render graph](https://docs.unity.com/en-us/engine/6000.6/manual/analysis/graphics-performance-profiling/in-urp/framebuffer-fetch/render-graph-framebuffer-fetch)
- [On-tile rendering](https://docs.unity3d.com/Manual/on-tile-rendering.html)
- [Universal Renderer: depth priming, depth texture mode](https://docs.unity3d.com/6/Documentation/Manual/urp/urp-universal-renderer.html)
- [URP asset](https://docs.unity3d.com/Manual/urp/universalrp-asset.html)
- [Optimise for untethered XR (tile GPUs)](https://docs.unity.com/en-us/engine/6000.3/manual/xr/graphics/untethered-device-optimization)
- [STP](https://docs.unity3d.com/Manual/urp/stp/stp-upscaler.html)
- [URP shader stripping](https://docs.unity3d.com/6000.2/Documentation/Manual/urp/shader-stripping.html)
- [PSO tracing](https://docs.unity3d.com/Manual/shader-pso-trace.html) · [Shader warm-up](https://docs.unity3d.com/6/Documentation/Manual/shader-prewarm.html) · [PSO tracing in Unity 6 (forum, Unity staff)](https://discussions.unity.com/t/prevent-shader-compilation-stutters-with-pso-tracing-in-unity-6/951031)
- [Mesh LOD](https://docs.unity3d.com/Manual/lod/mesh-lod-introduction.html)
- [Adaptive Probe Volumes](https://docs.unity3d.com/Manual/urp/probevolumes-concept.html)
- [SRP Batcher materials](https://docs.unity3d.com/6000.1/Documentation/Manual/SRPBatcher-Materials.html)
- [IL2CPP](https://docs.unity3d.com/cn/6000.0/Manual/il2cpp-introduction.html) · [macOS requirements](https://docs.unity3d.com/Manual/macos-requirements-and-compatibility.html)
- [macOS player settings](https://docs.unity.com/en-us/engine/6000.5/manual/platform-specific/apple-mac/player-settings-mac-os) · [enableMetalAPIValidation](https://docs.unity3d.com/ScriptReference/PlayerSettings-enableMetalAPIValidation.html)
- [Assembly definitions](https://docs.unity3d.com/Manual/assembly-definition-files.html)
- [URP 3D Sample](https://discussions.unity.com/t/introducing-the-new-urp-3d-sample/929894) · [Its quality settings](https://discussions.unity.com/t/urp-project-quality-settings-learn-from-the-urp-3d-sample/338359)

Apple:
- [Optimize Metal performance for Apple silicon Macs (WWDC20 10632)](https://developer.apple.com/videos/play/wwdc2020/10632)
- [Harness Apple GPUs with Metal (WWDC20 10602)](https://developer.apple.com/videos/play/wwdc2020/10602/)
- [Build GPU binaries with Metal (WWDC20 10615)](https://developer.apple.com/wwdc20/10615)
- [Game performance tools (Meet with Apple 242)](https://developer.apple.com/videos/play/meet-with-apple/242)

Games and cities:
- Cities: Skylines II: [Colossal Order developer on its BRG renderer](https://twt.omada.cafe/r/CitiesSkylines/comments/17ekhtw/comment/k64zldb/?context=3) · [CO on missing levels (TechRadar)](https://www.techradar.com/gaming/pc-gaming/no-cities-skylines-2s-performance-issues-arent-because-of-the-citizens-teeth-developer-confirms) · [Huhtala's analysis, summarised (Hot Hardware)](https://hothardware.com/news/cities-skylines-2-autopsy)
- Shadows of Doubt: [procedural interiors](https://colepowered.com/shadows-of-doubt-devblog-13-creating-procedural-interiors/) · [doors as culling portals](https://colepowered.com/?p=35092)
- Townscaper: [MCV interview](https://www.mcvuk.com/business-news/when-we-made-townscaper/)
- Megacity Metro: [Unity](https://unity.com/megacity)
- INSIDE, Firewatch, Sable, Genshin Impact, Obra Dinn and the rest: `reviews/unity-craft/notes-games.md`, every line with its URL.
