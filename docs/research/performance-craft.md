# Performance craft: a painted town at 60 fps on the M4

How to draw the town at 60 fps at 1440p on the M4 Mac mini: the clever ways, ranked by the milliseconds they should save on our measured costs, each with its cost to us, its risk to the look and its A/B on the harness. Game Lab research, 22 October, Opus 5.5, from reading online and from our own shaders and settings. It does not repeat `performance-at-scale.md` (levels, chunks, bakes, libraries, quality control), `tools-and-performance.md` or `scale-test.md`. The budget it works against is `docs/measuring.md`, The pass budget.

## In short

1. **Beams:** a quarter of the pixels, 16 steps, one hard shadow tap, clouds from a map: low sun −60 ms. Today 40 steps each run a 16-tap filter and the cloud noise.
2. **Shade each term at the rate it changes:** the town's sky (64 reads a pixel) per vertex, cached until history changes; clouds one small map a frame: −4 to −7 ms of the opaque pass's 12.5.
3. **Profile per line in Xcode** (M3 and later): names the rest in an afternoon.
4. **Trees:** depth first, then colour without `clip()`; the town's sky per vertex: the birch −8 to −13 ms.
5. **Keep the frame on tile:** one framebuffer fetch for the full-screen passes, the palette in the grade's LUT, no opaque texture, MSAA unstored: −4 to −6 ms.
6. **SSAO from depth at half size; SSR at half size, only when wet:** −3 to −5 ms.
7. **Band-limit procedural marks by footprint:** −1 to −2 ms, less shimmer (R2c).
8. **Render scale 0.85 with FSR 1, then dynamic resolution, as the reserve:** −3 to −5 ms.

Estimated together: blue hour 30 → about 13 ms; low sun 102 → about 19, or 15 with item 8.

## Where the time goes, and why

The street stop, offscreen ms at 1440p (`docs/measuring.md`, The pass budget; `reviews/lt1/playable/walk/w3-report.md`):

| Pass | Blue hour | Low sun | What the code shows |
| --- | --- | --- | --- |
| Sun beams | 1.0 | 64.3 (40 with no shadow map) | `SunBeams.shader`: 40 steps a pixel at full size; each calls `MainLightRealtimeShadow` under `_SHADOWS_SOFT_HIGH` (URP's 7×7 tent, 16 taps), picks a cascade, and evaluates the cloud field (seven value noises) and the haze's density |
| Opaque shading (bare 14.5, flat 1.9) | 12.5 | 12.5 | every Street, Stone and Tree pixel runs `OS_TownSky` (8 directions × 8 reaches: **64 map reads** and 8 `atan`), `OS_CloudLight` (the same seven-noise field), `OS_Brush`, and Stone's growth loops (3×3 cells, noise in each), computed whole and then faded by distance |
| The birch, where seen | | 12.6 | leaf cards with `clip()` and `Cull Off`, the same per-pixel `OS_TownSky` on every layer of leaves |
| MSAA 4× | 5.4 (1.8 empty) | 6.5 to 13.3 | 1.8 ms on an empty frame: the multisampled targets are stored and reloaded, not resolved on tile |
| SSAO, SSR | 2.4, 3.2 | 4.3, 3.9 | SSAO from DepthNormals (a second draw of everything) at full size; SSR 2.3 ms with nothing to reflect |
| Fog lights, key block, palette | 2.6 | 3.8 | `FullScreenPassRendererFeature` with `fetchColorBuffer`: a full copy each, about 0.5 ms even when idle |
| Busy output (R2c) | +2.2 on a busy screen | | paid in the passes after the draw |

**The M4 is a tile-based deferred renderer.** For opaque fragments that neither discard nor write depth, hidden surfaces are removed before shading, "entirely" (Apple, WWDC20 10631). So opaque overdraw is nearly free and a depth prepass buys nothing; Unity turns depth priming off on such hardware. What costs is every byte that leaves the tile. MSAA is meant to be cheap: samples live in tile memory, and the resolve store action writes only the resolved pixels (Apple Tech Talk 606). Any pass that samples the camera's colour or depth as a texture forces a store, four samples deep under MSAA.

**Its render targets are losslessly compressed** (Apple, Optimizing texture data; search excerpt). Flat colour compresses well and noise does not. That fits R2c: a quad writing texel-rate noise cost +2.2 ms with no texture read, paid in later passes. A busy image costs bandwidth in every pass that reads or writes the colour, and we have seven.

**In the shaders,** the opaque pass's 12.5 ms is per-pixel work, and its biggest item by the code, `OS_TownSky`'s 64 reads, has never been measured alone; the haze march, the first suspect, was 1.5 ms at most (`reviews/lt1/history/r2.md`). And small triangles that rasterise cheaply in a flat shader multiply an expensive one: GPUs shade in 2×2 quads, and the helper lanes at a triangle's edge run the full shader for nothing (`performance-at-scale.md`, What a pixel holds). The flat A/B cannot see this.

## Ranked by expected saving

### 1. The beams, at the cost they are worth (low sun −60 ms)

`docs/measuring.md` proposes a quarter of the pixels, 12 to 16 steps and one hard tap. The code shows why each matters, and adds one change.
- *One hard tap, not the soft filter.* 40 steps × 16 taps is 640 shadow taps a pixel: the 24 ms. A point in the air is lit or not; the beam's softness comes from the march and the blur. A local keyword drops `_SHADOWS_SOFT_*` in this pass, cutting the taps to a sixteenth.
- *The clouds from a map.* The cloud layer is a slowly changing 2D field. Render it once a frame into a 256² or 512² map over the town, and let the beams, the surfaces and the sky read it. This is most of the 40 ms the pass costs on an empty frame.
- *A quarter of the pixels and 16 steps,* blue-noise jitter, a depth-aware upsample and a small bilateral blur. Shafts have little internal contrast: NVIDIA's volume-light sample divides each side by four and warns only of edges at depth breaks. Genshin Impact marches its god rays at half by half over five cascades. Its froxel fog costs under 1 ms on a PS4, but its voxels were too coarse for god rays (Yi, Unity Dojo 2021): froxels alone will not cut our gaps between roofs. INSIDE kept very low sample counts clean with blue-noise dithering (GDC 2016; abstract only). Mitchell's screen-space radial blur (GPU Gems 3, ch. 13) is cheaper still but loses the shafts with the sun behind the viewer: a far fallback at most.

Expected 64 → 0.6 to 1.2 ms. Cost: two to three days. Look risk: grain or haloes at roof edges if the upsample is naive. A/B: `-beams`, then three keyword arms (hard tap, cloud map, quarter size) one at a time in low sun, judged on the golden frames and the motion sheets.

### 2. Shade each term at the rate it changes (opaque −4 to −7 ms, every light)

The scene runs on four clocks: the camera every frame, the clouds every second, the sun every minute of the scene's clock, the town every year of its history. Today all four are paid per pixel per frame. Compute each on its own clock, keyed to the scene's clock and the facts, never frame time, so the same inputs still give the same image and the golden views hold.
- *The town's sky,* 64 reads and 8 `atan` a pixel, changes only when buildings change. Compute it per vertex: our near meshes are dense enough to interpolate it within its own smoothness. Better, compute it once per chunk in a compute pass when the chunk's town changes and keep it as a vertex stream beside the bake, `performance-at-scale.md`'s "bake inputs" applied to a live input. For large ground triangles, a horizon map (eight horizon slopes per sky-map texel in two RGBA8 textures, two reads; Max 1988) is the fallback. Estimated 3 to 5 ms; item 3 will measure it.
- *Cloud shadow:* one read of item 1's map instead of the seven-noise field, called twice in look P: 0.5 to 1.5 ms.
- *Far shadows:* the town is static and the sun moves by the minute. Genshin updates four near cascades every frame and interleaves four far ones (each at least once in eight frames), and filters soft shadows only inside a quarter-size penumbra mask, which cut that pass from 2 to 2.6 ms to 1.3 to 1.7 (Yi 2021). URP has no cached cascades, so that is a custom pass; first take the cheap part: three cascades, a shorter distance, and soft quality Medium (a 5×5 tent against High's 7×7; URP 14 changelog). Unity's own advice is Low or off (Unity, Adjust settings). −2 to −4 ms of the 7 ms map in drizzle.
- *Skip work, do not fade it.* Stone's growth computes its near rosettes and then `lerp`s them away past the street stop; `OS_Near` fades near marks but still pays for them. Branch on the footprint instead: neighbouring pixels share it, so the branch is coherent, and M3-class heat maps show divergence if not.

Cost: three to five days in `StreetLooks.hlsl`, `StreetSurface.hlsl`, `Stone.shader` and a small compute pass. Look risk: none by design; each term is the same function evaluated elsewhere. A per-vertex sky shows only where a large triangle spans a sharp horizon change (check the lane's ground at the walls' feet). A/B: `OS_TOWNSKY_VERTEX` and `OS_CLOUD_MAP` arms; golden frames within a few levels.

### 3. Measure per line before guessing (an afternoon)

The opaque shading's owner is "unknown until L5", but the M4 can tell us directly. Xcode's Metal debugger profiles a captured frame per pipeline state and per line of shader source. On M3 and later it adds the shader cost graph (a flame graph of function calls) and heat maps of cost and divergence (Apple, Optimizing GPU performance). Unity's `FrameCapture.CaptureNextFrameToFile` writes the capture from the built player. One capture per light at the street stop ranks `OS_TownSky`, the clouds, the growth loops, the shadow filter and the light loop by share of samples. Its bandwidth counters show whether MSAA is stored (item 5). It replaces several harness runs of keyword arms; the harness then confirms each win. Cost: half a day to wire the capture into the runner, with shader source kept in the build.

### 4. Trees without shading every leaf twice (the birch −8 to −13 ms where seen)

Alpha-tested fragments defeat hidden-surface removal, because they "cannot write data to the depth buffer until the fragment shader has executed". Imagination advises drawing opaque, then alpha-tested, then blended (Imagination, Do not use discard; PowerVR forum). Our crowns run the full shader with `clip()` on every layer of cards, with `OS_TownSky` and the cloud noise each time, and `Cull Off` doubles the faces.
- *Depth first, for alpha-tested things only:* the crowns' `DepthOnly` pass with its cheap `clip()`, then colour with `ZTest Equal`, `ZWrite Off` and no `clip()`. The heavy shader runs once per visible leaf pixel. URP's depth priming cannot do this under MSAA, so it is a small renderer feature on a tree layer.
- *The town's sky and cloud light per vertex* in `Tree.shader`.
- *Fewer, fuller cards,* their outlines trimmed to the leaves, as Persson's Particle Trimmer fits polygons to a sprite's alpha to save fill-rate (Humus), round opaque inner lobes so cards cover only the edge.
- *Far off, impostors:* Fortnite draws upper-hemisphere octahedral impostors for trees when Nanite is off (Epic, Impostor Baker). Planned in `performance-at-scale.md` §3, with Firewatch's alpha-cutoff dial.

Cost: two to three days. Look risk: `ZTest Equal` needs identical positions in both passes, wind included. Alpha-to-coverage edges stay, since coverage stays on tile. A/B: the birch A/B at the street stop, 12 m and the city camera in low sun, after each change.

### 5. Keep the frame on tile (−4 to −6 ms, every light)

Unity's own rules for tile-based GPUs (Unity, Optimize for untethered XR devices; On-tile rendering): drop the opaque and depth textures, which cause extra copies; read the current pixel by framebuffer fetch (`SetInputAttachment`, Vulkan and Metal), not a copy; check every load and store in the Render Graph Viewer. Its Tile-Only Mode excludes MSAA, HDR and the depth texture, so it is not for us; its rules are.
- *The full-screen passes as one.* Fold fog lights and the key block into one render-graph pass that reads colour by framebuffer fetch, skipped when both are idle: 2.6 to 3.8 → 0.3 to 0.6 ms.
- *The palette into the grade's LUT.* If `Palette.shader` reads no neighbours, bake its colour function into the colour-lookup texture post already samples, once per style change, and it costs nothing per frame. A pull "into a few masses" that reads a neighbourhood cannot go in a LUT; check first.
- *Who reads the opaque texture?* None of our shaders sample `_CameraOpaqueTexture`. If URP's SSR does not either, `m_RequireOpaqueTexture` off removes a resolve and a full copy.
- *MSAA's store.* The usual causes are copy-depth after opaques (MSAA depth must then be stored) and passes after opaques that sample colour. Take depth from the prepass SSAO already forces (`Depth Texture Mode: Force Prepass`), so MSAA depth stays on tile.

Cost: two to three days. Look risk: none. A/B: `-foglights,-keyblock,-palette` and the empty frame's MSAA, before and after; golden views bit-identical.

### 6. SSAO and SSR at the size they read at (−3 to −5 ms)

`docs/measuring.md` proposes half size for both, and SSR only where wet. Two more steps. Take SSAO from depth (`Source: Depth`), which drops the DepthNormals draw of every triangle, with `Downsample` on. Genshin runs HBAO at half size with a bilateral upsample (Yi 2021), and our stone already takes only 0.2 of SSAO (`OS_OCCLUSION`). Then switch SSR off by the weather: dry hours have nothing wet to reflect, and its empty-frame cost is 2.3 ms. Genshin's SSR costs about 1.5 ms on a PS4 Pro, so a half-size, wet-only SSR near 1 ms is a fair line. Cost: a day. Look risk: AO halos at depth breaks with a naive upsample. A/B: `-ssao`, `-ssr` in drizzle and the blue hour.

### 7. Busy output: band-limit the procedural marks (−1 to −2 ms, less shimmer)

A procedural mark finer than a pixel adds nothing the eye can read. It adds aliasing, shimmer in motion and R2c's bandwidth. The fix is filtering procedurals: drop each octave whose period falls below about two pixels, by the footprint we already compute (Quilez, Band-limiting; Dorn et al. 2015). `OS_Near`, the paving's `far` and the water's flattening do this in places. Make it a rule for every noise call (`OS_Brush`, `OS_Carve`, the stone's crumb, sand and craze, the bark) and skip each dropped octave's work. Where a mark can be a tiling texture instead of hashes (brush and carve are world-fixed patterns), the mip chain band-limits it for free. Cost: one to two days. Look risk: low; this is "painted from afar" in code. A/B: R2c's `noisy` quad against a band-limited one, then the street stop.

### 8. Fewer pixels, as a dial, not the fix (−3 to −5 ms after the rest)

About two thirds of the frame scales with pixels; a render scale of 0.85 shades 72% of them. URP 6.6 upscales by bilinear, nearest, FSR 1 or STP; FSR 2, DLSS and MetalFX are not in URP (Unity, Changing resolution scale), so MetalFX would need a native plugin. STP needs temporal anti-aliasing and excludes dynamic resolution (Unity, STP), which conflicts with our no-temporal decision and the golden stills. Dynamic resolution works on macOS, Metal only (Unity, Dynamic resolution).

The painted look tolerates it. Tears of the Kingdom renders up to 900p, nearer 720p in motion, upscaled by FSR 1, and still uses FSR 1 at up to 1440p on Switch 2 (Digital Foundry, via Nintendo Life and Nintendo Everything). A Short Hike was built to need as few pixels as possible (PlayStation Blog). Our risk is the near tier, "true up close": joints, glazing bars and the key block's lines shimmer first. Keep 1.0 for judging. Use a fixed 0.85 with FSR 1 only if a view still misses 16.7 ms after items 1 to 7, and dynamic resolution driven by `FrameTimingManager` against spikes. A/B: `-perf-offscreen-scale` at 0.8 and 0.85; golden views upscaled, judged on the shimmer measure.

### 9. Smaller items

- *Post in low sun,* 2.8 to 4.7 ms against about 1: likely bloom on a bright sky. Turn off its high-quality filtering and start from a smaller first mip; item 3 confirms.
- *Half precision.* On M3 and later, FP16 runs at peak rate with fewer registers, and FP16, FP32 and integer work issue side by side; dynamic caching stops peak register use from capping occupancy (Apple, GPU advancements in M3 and A17 Pro). Our shaders are mostly `half`; hashes and positions rightly stay `float`.
- *Levels cut shading, not only raster.* With an expensive shader every edge sample and helper lane runs it, so part of MSAA's 5 to 13 ms and of the opaque pass falls as levels reach ten-pixel triangles. Measure it by profiler samples, not the flat arm.
- *Out of reach on Metal from Unity:* variable rate shading (Unity's API is DirectX 12 and Vulkan), rasterization rate maps and lossy render-target compression (not exposed), depth input attachments (DirectX 12 and Vulkan).

## The frame after these, estimated

The street stop, ms; estimates until each item is A/B'd.

| Pass | Blue hour today | Low sun today | After items 1 to 7 |
| --- | --- | --- | --- |
| Opaque shading and raster | 14.5 | 14.3 | 5 to 7 |
| Beams | 1.0 | 64.3 | 0.6 to 1.2 |
| Sun's shadow map | | 7.4 to 8.4 | 3 to 4 |
| MSAA 4× | 5.4 | 6.5 to 13.3 | 2 to 4 |
| SSAO, SSR | 5.6 | 8.2 | 1 to 2 |
| Full-screen passes | 2.6 | 3.8 | 0.3 to 0.6 |
| Post, sky | 2.7 to 3.6 | 5 to 6 | 2 to 3 |
| **Frame** | **30.0** | **102.1** | **about 13 (blue hour), about 19 (low sun)** |

Low sun still misses by about 2 ms: item 8 closes it, or the shadows go further (cached far cascades, proxy casters). The birch adds 1.5 to 3 ms where seen after item 4.

## Order

The plan's frame-rate gate owns this (`docs/plan.md`). The proposed order, by saving over cost: item 3 first, because it turns item 2's estimates into numbers; then 1 (1c's beams); 2 and 5 together (one pass over the shared includes and the renderer); 4 (1e's birch); 6; 7; 8 only if a view still misses. Each lands with its harness A/B, and with bit-identical golden views where the look is meant not to change.

## Gaps

- No first-hand rendering talk was found for SEASON (its Unreal blog returned 403), Sable, Tunic, Townscaper, Outer Wilds or Firewatch's fog. Breath of the Wild is known only through Digital Foundry's resolution counts. Genshin's mobile renderer is unpublished; its console talk stands in.
- The AC4, INSIDE and Firewatch slides could not be read past their abstracts.
- Whether URP 6.6 keeps our MSAA attachments memoryless, and whether its SSR reads the opaque texture, wait for the Render Graph Viewer or a capture.
- `OS_TownSky`'s cost is estimated from its code, not measured.

## Sources

Apple: [Tailor your apps for Apple GPUs and TBDR](https://developer.apple.com/documentation/metal/tailor-your-apps-for-apple-gpus-and-tile-based-deferred-rendering) · [Bring your Metal app to Apple silicon Macs (WWDC20 10631)](https://developer.apple.com/videos/play/wwdc2020/10631/) · [Imageblock sample coverage control (Tech Talk 606)](https://developer.apple.com/videos/play/tech-talks/606/) · [Explore GPU advancements in M3 and A17 Pro](https://developer.apple.com/videos/play/tech-talks/111375/) · [Optimizing GPU performance (Xcode)](https://developer.apple.com/documentation/xcode/optimizing-gpu-performance) · [Optimizing texture data](https://developer.apple.com/documentation/metal/optimizing-texture-data) (search excerpt) · [Imagination: Do not use discard](https://docs.imgtec.com/starter-guides/powervr-architecture/html/topics/rules/do-not-use-discard.html) (search excerpt) · [PowerVR forum: HSR and blending](https://forums.imgtec.com/t/hidden-surface-removal-for-alpha-blended-fragment-under-opaque-one/1585) (search excerpt)

Unity: [Optimize for untethered XR devices in URP (6000.6)](https://docs.unity.com/en-us/engine/6000.6/manual/xr/graphics/untethered-device-optimization) · [On-tile rendering (6000.6)](https://docs.unity.com/en-us/engine/6000.6/manual/analysis/graphics-performance-profiling/in-urp/on-tile-rendering) · [Framebuffer fetch in render graph](https://docs.unity.com/en-us/engine/6000.6/manual/analysis/graphics-performance-profiling/in-urp/framebuffer-fetch/render-graph-framebuffer-fetch) (search excerpt) · [Universal Renderer: depth priming](https://docs-alpha.unity3d.com/Manual/urp/urp-universal-renderer.html) (search excerpt) · [Changing resolution scale](https://docs.unity.com/en-us/engine/6000.6/manual/cameras/resolution-scale/introduction) · [Dynamic resolution](https://docs.unity.com/en-us/engine/6000.6/manual/cameras/resolution-scale/dynamic-resolution/introduction) · [STP](https://docs.unity3d.com/Manual/urp/stp/stp-upscaler.html) (search excerpt) · [Adjust settings for performance in URP](https://docs.unity.com/en-us/engine/6000.5/manual/analysis/graphics-performance-profiling/in-urp/optimize-for-better-performance) · [URP 14 changelog: soft shadow filters](https://docs.unity3d.com/ja/Packages/com.unity.render-pipelines.universal@14.0/changelog/CHANGELOG.html) (search excerpt) · [Variable rate shading](https://docs.unity.com/en-us/engine/6000.6/manual/analysis/graphics-performance-profiling/in-urp/variable-rate-shading/implementation) (search excerpt) · [FrameCapture](https://docs.unity.com/en-us/engine/6000.0/script-reference/unityengine/apple/framecapture)

Games and craft: [Genshin Impact on console, Zhenzhong Yi, Unity Dojo 2021](https://docswell.com/s/UnityJapan/KWRPQ5-210617-unity-dojo20211mihoyozhenzhongyi) · [Digital Foundry on Tears of the Kingdom (Nintendo Life)](https://www.nintendolife.com/news/2023/05/video-digital-foundrys-technical-analysis-of-zelda-tears-of-the-kingdom) · [Digital Foundry on Switch 2 (Nintendo Everything)](https://nintendoeverything.com/zelda-breath-of-the-wild-and-tears-of-the-kingdom-nintendo-switch-2-frame-rate-resolution/) · [A Short Hike (PlayStation Blog)](https://blog.playstation.com/2021/08/05/crafting-a-tiny-open-world-a-look-behind-the-scenes-at-the-creation-of-a-short-hike/) · [INSIDE rendering, GDC 2016](https://gdcvault.com/play/1023002/Low-Complexity-High-Fidelity-INSIDE) (abstract) · [GPU Gems 3, ch. 13](https://developer.nvidia.com/gpugems/gpugems3/part-ii-light-and-shadows/chapter-13-volumetric-light-scattering-post-process) (outline) · [NVIDIA Volume Light](https://developer.download.nvidia.com/SDK/10.5/direct3d/Source/VolumeLight/doc/VolumeLight.pdf) (search excerpt) · [Wronski, AC4 GDC 2014](https://bartwronski.com/2014/03/09/my-upcoming-gdc-2014-presentation/) (preview) · [Particle Trimmer (Humus)](http://www.humus.name/index.php?page=Cool&ID=8) · [Impostor Baker (Epic)](https://dev.epicgames.com/documentation/unreal-engine/impostor-baker-plugin-in-unreal-engine) (search excerpt) · [Quilez, Band-limiting](https://iquilezles.org/articles/bandlimiting/) (search excerpt) · [Dorn et al. 2015](https://diglib.eg.org/handle/10.1111/cgf12747) (abstract) · [Horizon mapping (Max 1988)](https://en.wikipedia.org/wiki/Horizon_mapping) (search excerpt)
