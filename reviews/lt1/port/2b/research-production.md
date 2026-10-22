# Stone: the production craft and its cost

Research for the stone redraw (Q15), 22 October, Opus 5.5, online only. It adds to `docs/research/` and the sibling `research-restraint.md` without repeating them. Summaries, forums and memory are marked (secondary); unconfirmed claims and our arithmetic (unverified). A pixel covers about 0.6 mm per metre with the walker's lens.

## In short

1. **Unique baked detail on every stone needs virtual texturing or Nanite; URP has neither.** Studios bake uniquely only for heroes. At 1 mm a texel three unique maps cost about 4 MB per square metre of face: about 240 MB for a flight and its cheeks (about 60 m²; unverified).
2. **Studios fit library stones by sizing the space, not the stone:** whole bricks, footprints in multiples, stairs in start, middle and end, booleans, or bent modules (forbidden here). None gives a slab exactly a step's width. That needs a fitted block with shared surface detail.
3. **Build the hybrid:** a light rigid block per stone, cut to its fact size, real chamfers, weighted normals; its surface from a few shared sculpted face textures per kind and working, picked and offset per stone. This is Star Citizen's "med poly" method (secondary) and The Order: 1886's tiling library, with our generator fitting. A box chamfered with one segment has 24 vertices and 44 triangles: a hard-edged box's vertex count, with no split normals.
4. **Near-tier aim:** 150 to 400 triangles a step (mostly the tread grid that carries the hollow) and 30 to 120 a wall stone with hidden faces deleted. A 30-step flight comes to about 9,000 and 90 m of cheek wall to 60,000–130,000, against today's 962,000 (unverified).
5. **Small and thin triangles are the M4's real cost.** Apple: "Render fewer very small triangles, especially if you're applying MSAA as well" (we run 4×). Thin chamfer strips span more tiles; they leave the mesh past about 10 m.
6. **Wear by vertex fields and height blends is nearly free a pixel; decals, parallax occlusion and triplanar are not.** Unity recommends screen-space decals on tile GPUs. Our stones carry metric UVs and need no triplanar.
7. **Instancing is for identical repeats, not fitted stones.** The GPU Resident Drawer saves CPU and "slightly increases GPU workload". Fitted stones merge into chunks; Mesh LOD keeps its levels in the original index buffer, so (our reading) per-vertex history survives decimation. Shadows come from a street-tier proxy.

## 1. Where the detail lives

**a. Unique high poly, baked per stone.** Firewatch's rocks were sculpted and baked (`stone.md`); DICE's Battlefront photogrammetry and Megascans do it at scan quality. Book of the Dead gave large rocks object-space normal maps so LOD switches would not show, at some cost in precision (Heijmans, Unity). Perfect at 1–5 m, wasted at 12 m, and every stone needs its own maps. Heroes only, such as a dated carved stone.

**b. A sculpted library, instanced.** Karl Aldskogius (80.lv) built a stone kit high to low, kept each stone's texture low in contrast "to avoid having too much uniqueness per stone", and baked a tileable from the same stones so kit and tileable match. Fabien Burger's Houdini wall uses three bricks differing only in "bevel seeds". Finn Bogaert built a UE5 stair from two sculpted rocks in instanced modules (secondary). Cyberpunk pushes a detailed stone mesh into a bevelled box (Schreibt, secondary). Store packs list 300 to 1,300 triangles a rock at LOD0; a photoscanned wall 6,000 at LOD0 and 1,600 at LOD2 (vendors). Light on memory and good at every distance, but it fails our facts: a step must be its own size, and a turned library stone cannot carry a chamfer placed by a fact.

**How studios fit.** Burger rounds a 5.5 m wall to 5.4 m for 0.3 m bricks. Bethesda keeps footprints in multiples; Kronenberger splits stairs into start, middle and end (`kits-and-generation.md`). Julian Elwood used "rapid booleans and auto placement of bricks" in Houdini for The Last of Us Part I (Gnomon). Aldskogius bent a strip of stones, which our rule forbids. A dressed piece with sculpted ends (a coping's end, a returned nosing) can be three-sliced: ends at size, a straight prism between them lengthened along its axis with metric UVs, which bends nothing (unverified as studio practice; ChipWits slices walls this way).

**c. A light chamfered block with shared texture.** Star Citizen used a "med poly" model with many chamfers and custom normals, tiling materials and decals (Polycount, secondary). The Order: 1886 kept a library of "highly crafted tiling materials" from 3D sculpts (Phail-Liff and Vitale, SIGGRAPH 2015). Gears of War 4 let artists "layer dozens of materials" and "cook out the results in-engine for efficient run-time performance" (Penty and Wong, SIGGRAPH 2017). Each stone takes a random offset and turn into a tileable sculpt, or a patch from an array. It holds at 1–5 m with face textures at 0.5–1 mm a texel and real chamfers; at 12 m the mips do the work and the chamfer strips should be gone. Its weakness is a shared face's big features recurring: several patches per kind and low contrast answer it.

**d. Trims** (Insomniac's Ultimate Trim, `stone.md`) suit copings, kerbs and a nosing's long face: tooling runs along a strip mapped in metres, while the real chamfer carries the edge.

**e. Kits** are in `kits-and-generation.md`. For Ghost of Tsushima, Sekiro, Elden Ring, Kena, Sea of Thieves, The Witness and Hellblade we found no stair or wall breakdown we could open: a gap. Valley of the Ancient is about 90% Megascans, all Nanite, no LODs (Epic): not transferable.

## 2. Wear and history by masks

| Technique | Who | Cost a pixel on a tile GPU |
| --- | --- | --- |
| A vertex channel per layer (cracks, moss, wet) | The Last of Us Part I (Benainous, secondary); Uncharted 4's moss and wetness shading | one interpolant. Needs vertices where the mask changes: Aldskogius adds quads only so vertex paint interpolates evenly |
| A smooth field per vertex, a ragged edge by noise | Tiny Glade | one interpolant, one noise fetch |
| Height blend | Mishkinis; Book of the Dead's terrain | no extra fetch if height rides in alpha |
| Baked layers | Gears of War 4; our "bake inputs" | one fetch of a chunk map |
| World mask | The Division | one fetch |
| Mesh decal | Star Citizen; Fallout 3 | a small extra draw, no depth read |
| URP screen-space decal | Unity | 1, 3 or 5 depth reads (normal blend Low, Medium, High); needs the depth texture |
| URP DBuffer decal | Unity | a DepthNormal prepass; Unity recommends screen space on tile GPUs |
| Parallax occlusion | | 8 to 32 fetches; with depth offset it writes depth, which "can incur a performance penalty" (Apple) |
| Triplanar, biplanar | Quílez | three or two times every fetch |

Each varying costs tiled-vertex-buffer space and interpolation (an Apple limiter), so keep fields packed as `channels.json` does. Vertex fields say where, height blends how it ends; a dated event (a screed, an indent) is geometry or a mesh decal.

## 3. Cost on our stack

**Small and thin triangles.** Apple's line is in In short 5. Arm: hardware rasterisers "often struggle with small or thin triangles", and "Long, thin triangles can span multiple tiling bins"; ten fragments a triangle is Arm's old low-water mark (secondary). Meta: binning re-runs position work per tile touched, so make triangles "fat". A 6 mm chamfer is about 2 px wide at 5 m and 0.9 px at 12 m, so along a 40 cm strip most of each 2×2 quad is helper lanes (unverified).

**The tiled vertex buffer.** The Apple GPU runs a pass's vertex work first and stores it; when the buffer fills, partial renders "require tremendous memory bandwidth" (Rosenzweig, from Apple's WWDC material). Each shadow cascade is another geometry pass over its casters (our inference).

**Shadows.** Unity's `ShadowsOnly` mode lets an invisible street-tier proxy cast while the near mesh casts none. Book of the Dead stopped small vegetation casting at 15 m. The proxy must keep the nosing line, or each step's shadow on the step below shifts (unverified).

**Instancing and LOD.** The Resident Drawer groups only shared meshes; our cost is GPU triangles, so it suits setts, not fitted stones. Mesh LOD selects by screen size and "stores each LOD in the index buffer of the original mesh"; its cross-fade needs the Resident Drawer, and it should not be mixed with LOD Group. Book of the Dead found LOD cross-fade "quite heavy" in draw calls.

**Memory (unverified).** A chamfered block is about 1.3 KB at 44 bytes a vertex; a 300-triangle stone about 10 KB; 5,000 stones 7–50 MB. A shared face kind at 0.5 mm a texel over a 1 m tile, in BC7 (albedo, height) and BC5 (normal), is about 11 MB with mips, however many stones use it. Apple's advice: bilinear rather than trilinear where it holds, compressed formats.

## 4. For our generator

**Choose c, with b for rare features and d for long pieces.**

- **Each stone:** a rigid block cut to its fact size; planar faces; a chamfer on each arris from its working and wear, never under 2 px at the nearest view (`research-restraint.md`); weighted normals; faces in contact or buried deleted; no edge noise.
- **Face detail:** 8 to 16 sculpted patches per kind and working (split, pitched, punched, tooled, sawn) in a texture array; each stone picks patch, offset and turn by seed, metric in `uv0`.
- **Library geometry only at a fact's place:** a spall, a chip, an indent, joined by a rigid boolean.
- **Tiers:** at the street tier chamfer strips go, the arris moves into normal and specular filtering, courses merge; a city-tier flight is about 2,000 triangles (`foundations.md`).

**What a lead technical artist would flag.**

1. Per-vertex history buys density only where a field varies: treads and the damp foot, never a riser's back or a buried bed.
2. Chamfer strips are slivers. Use one segment and fanned corners; check a median triangle of at least 10 px (`performance-at-scale.md`).
3. Unique meshes never instance: count bytes per kilometre and stream by chunk.
4. Custom normals are "fragile in the pipeline" (Polycount, secondary): import, never recalculate, and test the round trip. Derivative tangent frames get noisy on tiny triangles.
5. Shadows from proxies.
6. `GeometricNormalFiltering` (Tokuyoshi and Kaplanyan) is in our Core package's `CommonMaterial.hlsl`, and none of our shaders calls it: a few ALU against the one-pixel gloss lines.
7. A texture array, not an atlas, so mips do not bleed between patches (unverified).
8. The patch comes from the seed, so a stone looks the same until its history changes.

## Sources

- Apple: Reducing shader bottlenecks; Tailor your apps for Apple GPUs and TBDR; Calculating primitive visibility using depth testing. developer.apple.com
- Alyssa Rosenzweig, The Apple GPU and the Impossible Bug. alyssarosenzweig.ca/blog/asahi-gpu-part-5.html
- Arm, Mali and Unreal Engine's Nanite. developer.arm.com/community/arm-community-blogs/b/mobile-graphics-and-gaming-blog/posts/mali-and-unreal-engine-s-nanite-enabling-the-future-of-mobile-graphics
- Meta, GPU impaired algorithms. developers.meta.com/horizon/documentation/native/android/gpu-impaired-algorithms/
- Unity: Decal Renderer Feature reference; GPU Resident Drawer performance; Mesh LOD introduction; ShadowCastingMode. docs.unity3d.com
- Julien Heijmans (Unity), Book of the Dead: content optimisation tricks. unity.com/blog/industry/book-of-the-dead-quixel-wind-scene-building-and-content-optimization-tricks
- Karl Aldskogius (80.lv), Breakdown: a detailed and vibrant scene. 80.lv/articles/breakdown-creating-a-detailed-and-vibrant-scene-with-unreal-engine-and-substance-3d
- Fabien Burger (80.lv), Procedural wall generator in Houdini. 80.lv/articles/creating-a-procedural-wall-generator-for-unreal-in-houdini/
- Gnomon, Julian Elwood on Naughty Dog. gnomon.edu/news-and-events/news/gnomon-graduate-julian-elwood-on-environment-art-naughty-dog-and-teaching-at-gnomon
- Finn Bogaert, stair (search excerpt). finnbogaert.artstation.com/projects/y4vyAO
- Polycount, Star Citizen and custom normals threads. polycount.com/discussion/comment/2332892
- Phail-Liff and Vitale, Crafting Victorian London, SIGGRAPH 2015; Penty and Wong, Gears of War 4 layered materials, SIGGRAPH 2017. history.siggraph.org
- Brinck and Maximov, Technical Art of Uncharted 4. advances.realtimerendering.com/other/2016/naughty_dog/
- Tokuyoshi and Kaplanyan, Stable geometric specular antialiasing, JCGT 2021. jcgt.org/published/0010/02/02/
- Íñigo Quílez, Biplanar mapping. iquilezles.org/articles/biplanar
- Epic, Valley of the Ancient. dev.epicgames.com/documentation/en-us/unreal-engine/valley-of-the-ancient-sample-game-for-unreal-engine
- ChipWits, 9-slicing walls. chipwits.com/2023/05/06/9-slicing-walls/
- Unity Asset Store: Porous Rocks and Boulders; Photoscanned Modular Church Pack.
