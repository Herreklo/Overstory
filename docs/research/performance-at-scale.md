# Performance at scale and quality control

How the best studios build large worlds at quality and at a sane cost, and what that means for Overstory. Our case: a painterly-realist town in Unity 6 URP (6000.6, no Nanite), every part made by Python generators in Blender, a free camera from eye level in a lane to a near-isometric view, and later cities the size of London. Part of the Game Lab research. Drafted on Opus while Fable was out; a lead technical artist's bar.

Three sibling studies sit beside this one and are not repeated here: materials, surface history and the painterly look (`docs/research/materials-at-scale.md`), modular kits and procedural generation (`docs/research/kits-and-generation.md`), and environmental storytelling and weathering (`docs/research/history-in-things.md`). This page covers performance and quality control. Claims seen only in a summary are marked (secondary), unconfirmed ones (unverified). Numbers about our own work were measured on 21 October from the files named; estimates say so.

## In short

- **The style's distance rule and the budget's distance rule are one rule.** "True up close, painted from afar" (`docs/visual-direction.md`) is also what every large game does to survive: real geometry where a pixel can hold it, painted detail past that. Firewatch lowers its trees' alpha cutoff with distance so they read puffier and more stylised; Ghost of Tsushima blends grass normals to a shared clump normal far off (secondary); GTA V draws whole districts as one mesh. Our `OS_Near` already fades the shader's detail between 2.5 and 8 m. The geometry should follow the same curve. Today it does not.
- **Our stone is drawn at its eye-level detail at every distance.** One stair with its cheek walls is 816,206 triangles, about a fifth of the whole frame budget, in four meshes, one of them 33 m long. Past about 8 m most of those triangles are smaller than the 2×2 pixel blocks a GPU shades in, so the heaviest shader we have (`Stone.shader`) runs several times per pixel for nothing.
- **No game we found draws setts, tiles or bricks as geometry at a distance.** They use real pieces near the camera and at silhouettes, then tiling or baked materials with layers, parallax and decals. The Order: 1886 used 90 to 95% tiling materials with up to four runtime layers. Our version bakes our own near-tier pieces into each chunk's maps, so the street and city tiers draw the same stones and claim nothing new.
- **Bake inputs, not outputs.** Unreal's HLOD and Simplygon bake a material's result. We should bake the history channels (polish, lichen years, moss, water, years, seed), so weather, the hour and the season stay live at every tier and one shader draws them all.
- **Unity 6.6 has the pieces, not the system.** The GPU Resident Drawer, BatchRendererGroup, Renderer Shader User Value (one 32-bit value per renderer, no material copies), Mesh LOD and GPU occlusion culling all exist. There is no HLOD and no virtual texturing in URP. We build chunking, levels and bakes in our generators.
- **Shadows break first.** Cities: Skylines 2 spent about 40 ms of a frame and 72% of its draw calls on shadows; GTA V spends about a quarter of its draws there. Our shadows reach 200 m in four cascades of one 4096 shadow map, and every stone casts.
- **Disk and memory, not only frame time, rule out unique pieces everywhere.** One stair with its walls is 36 MB of FBX; the stone folder is 272 MB; `.git` is 2.2 GB. At the current density a kilometre of wall is about 5 million triangles. Repeated small pieces (setts, wall stones, slates, bricks) must come from approved libraries placed as instances, which is the project's own rule for parts.
- **Quality control at scale is cheap to start.** Frostbite keeps 32,849 reference screenshots and compares them pixel by pixel with NVIDIA's FLIP at "extremely stringent" thresholds; Unity's own URP tests run on Metal Mac minis like ours. A frame-time harness on fixed camera paths, a dozen golden views, mesh hashes and import checks can all be built now in Unity batch mode in about two weeks.

## Where we stand

Measured from `unity/Assets/Art/Stone/` and the generators on 21 October.

| What | Measured |
| --- | --- |
| Gully steps, flight 0 | 29 steps, 10.2 m run, 97,985 triangles, 51,250 vertices; about 3,000 triangles a square metre, 3,400 a step |
| Gully steps, flight 1 | 45 steps, 33.4 m run with landings, 263,297 triangles, 135,629 vertices; one mesh 33 m long |
| Cheek walls, both flights | 454,924 triangles over about 90 m of wall: about 5,000 a metre (6,100 on flight 0) |
| One stair with its walls | 816,206 triangles, 459,026 vertices before Unity splits them at sharp edges; 72 bytes a vertex (position, normal, six UV channels), so about 40 to 50 MB of vertex and index data on the GPU (estimate) |
| Parts (`slab.py`, `sett.py`, `wallstone.py`) | a slab 400 to 1,100 triangles; a sett 72 (about 50 setts a square metre, so 3,500 to 4,000 triangles a square metre); a wall stone 70 to 130 |
| On disk | `stone_gully.fbx` 16 MB, `stone_gully_cheeks.fbx` 20 MB, the 11 variety flights 210 MB; all tracked in plain git (no LFS); `.git` 2.2 GB |
| URP settings (`PC_RPAsset`, `PC_Renderer`) | Forward+, SRP Batcher on, GPU Resident Drawer off, GPU occlusion off, small-mesh culling 0, MSAA 4×, shadows to 200 m in four cascades at 4096, LOD cross-fade dithering on, static batching off |
| `Stone.shader` | `#pragma target 3.5`, no `DOTS_INSTANCING_ON`, no LOD cross-fade; history in UV1 to UV5 per vertex; lichen and moss each loop over 3×3 cells with noise per cell |
| Foundations' budget (`docs/foundations.md`) | a stone piece 600 triangles near and 120 at the street tier; a flight about 2,000 at the city tier; 4 million visible triangles and under 3,000 draws a frame at 1440p and 60 fps on a mid-range card |
| The dev machine | Mac mini, Apple M4 with a 10-core GPU. About 3.8 TFLOPS and 120 GB/s against an RTX 3060's 12.7 TFLOPS and 360 GB/s; 3DMark Steel Nomad Lite puts the 3060 at about 2.2 times the M4 (secondary, NanoReview) |

So against the foundations, a slab is up to twice its near budget, and a flight is about 130 times its city budget because it has no city tier at all. Draw calls are not our problem: the corner is a handful of very heavy draws. Triangles, shadows and memory are.

## What a pixel holds

Every decision below rests on one piece of arithmetic. At 2560 by 1440 with the street stop's 35 mm lens (about 38° vertical), one pixel covers about 0.48 mm per metre of distance. A longer lens at the far stop covers less per pixel.

| Distance | One pixel covers | What still reads as shape |
| --- | --- | --- |
| 1 m (eye level, at your feet) | 0.5 mm | a chipped arris, the crumb of a lichen crust |
| 2.5 m | 1.2 mm | `OS_Near` is still 1: every near mark is drawn |
| 8 m | 4 mm | `OS_Near` reaches 0; a 6 mm rounded arris is about 1.5 pixels |
| 20 m (the end of the near tier) | 1 cm | a 1 cm joint is one pixel; a sett is 12 pixels across |
| 35 m (the middle stop) | 1.7 cm | a step's 17 cm rise is 10 pixels |
| 80 m (the end of the street tier) | 3.8 cm | a rise is 4 pixels; a sett 3 |
| 120 m (the far stop, longer lens) | about 4 cm | a house front is about 250 pixels wide |
| 400 m | 19 cm | a 10 m house is about 50 pixels wide |
| 1.5 km (the horizon from the close stop) | 72 cm | a house is a dozen pixels |

GPUs shade pixels in 2×2 blocks. A triangle that covers one pixel still pays for four, and the waste "can really mount up with small triangles" (Self Shadow). Fatahalian and others measured that merging those blocks cut shading by about a factor of eight for pixel-sized triangles (secondary). Android's guidance calls triangles under 1 to 10 pixels micro triangles and prescribes LOD for distant objects. Nanite exists because hardware rasterisers do badly on them; its software rasteriser is cited at about three times the hardware's throughput for pixel-sized triangles (secondary).

Our stone at 2,500 to 4,000 triangles a square metre gives, on a face turned to the camera, about 20 pixels a triangle at 8 m and 3 at 20 m. On the lane's ground seen from the street stop the foreshortening cuts that by three to seven times: 7 pixels a triangle at 8 m, under 1 at 20 m. So the near pieces are right up to about 8 m and wasteful beyond. That is where `OS_Near` already lets go.

Two rules follow, and the rest of this page applies them.

1. **Choose a level by its error in pixels, not by metres.** A level whose shape is off by e metres is safe wherever one pixel covers more than e. With the 35 mm lens that is about 2,000 × e metres away: 2.5 mm of error from 5 m, 1 cm from 20 m, 4 cm from 80 m. Unity's LOD Group and Mesh LOD both select by screen size, so a longer lens is handled for free once each level knows its error.
2. **Keep the median visible triangle at ten pixels or more.** It is a measure, not a law, and the harness should report it.

The street and city tiers each span a factor of four or five in distance, so a triangle shrinks by 16 to 25 times in area across one; the near tier spans more. The near and city tiers each need two levels inside them: near as *close* (to about 8 m, with `OS_Near`) and *near* (8 to 20 m); city as *city* (80 to 200 m) and *district* (200 m and beyond).

## 1. Geometry at scale in Unity 6 URP

### What Unity 6.6 gives us

**The GPU Resident Drawer** turns ordinary MeshRenderers into instanced draws through the BatchRendererGroup API. It needs Forward+, the SRP Batcher, compute shaders, and shaders that support DOTS instancing; for a hand-written shader that means `#pragma target 4.5` or higher, a `multi_compile _ DOTS_INSTANCING_ON` and at least one block of DOTS-instanced properties. It refuses objects that use `MaterialPropertyBlock` or per-instance callbacks such as `OnRenderObject`. Unity says it "improves CPU performance, but it slightly increases GPU workload", that GPU-bound projects can get slower, and that merged instanced draws can add overdraw; it suggests depth priming against that. In Unity 6 depth priming is forced off when MSAA is on, and we run MSAA 4×. One user saw draws fall from 1,788 to 1,502 while CPU time rose from 5.8 to 6.1 ms; Unity staff replied that the gain depends on the view and the hardware (secondary). It pays when many objects share one mesh: kit parts, street things, tree clumps. It does nothing for a flight of unique slabs merged into one mesh. Unity 6.6 adds a Profiler card for its coverage, culling and LOD.

**Renderer Shader User Value** (Unity 6.3 and later) gives every renderer one 32-bit integer, read in HLSL as `unity_RendererUserValue`. It "doesn't require any material duplication, which avoids breaking GRD instancing draw calls". One integer is enough to index a `GraphicsBuffer` of per-thing facts (years, keeper's care, season, hue, wind phase). This is how history reaches instanced parts without breaking batching.

**BatchRendererGroup used directly** is for things too many to be GameObjects: setts, roof slates, grass. Instance data lives in a `GraphicsBuffer` that stays on the GPU; each DOTS-instanced property arrives as a 32-bit offset into it. RedLynx's GPU-driven pipeline, shown in the same SIGGRAPH 2015 course as Assassin's Creed Unity, drew 250,000 separate moving objects with two indirect draws, 2.3 ms of GPU time and 0.2 ms on a single Jaguar CPU core, the CPU of that console generation. Unity's BRG is not that pipeline, but it is the door to it.

**Entities Graphics** drives Megacity (widely quoted at 4.5 million mesh renderers; unverified). Cities: Skylines 2's experience suggests the glue between DOTS and rendering is the hard part: its author thinks Colossal Order built its own culling, skinning and texture streaming around it. We do not need Entities for a town; GameObjects through the Resident Drawer plus BRG for the swarms is enough.

**GPU occlusion culling** tests each object's bounding sphere against this frame's and last frame's depth. Unity warns that "thin or elongated objects have a much coarser spherical representation than their actual mesh" and that a scene with little occlusion can get slower. A 33 m flight in one mesh has a sphere about 34 m across and will never be culled. In a lane at eye level most of the town is hidden and occlusion pays; from the far stop almost nothing is hidden.

**Mesh LOD** (6.2 and later) builds levels at import, each with about half the indices of the one before, inside the mesh's own index buffer, without new vertices. It starts only on meshes of 256 triangles or more and stops at about 64. It "works best for organic shapes or relatively flat surfaces with a high vertex density" and "might produce undesired results on meshes with a high curvature". Static batching, classic GPU instancing and Entities always draw level 0; cross-fade works only with the Resident Drawer; combining it with LOD Group is "not recommended". The page says nothing about how it treats UV channels or seams. It is worth one afternoon's test on the gully's FBX. It cannot keep each piece's borders, so joints are likely to melt and history to smear.

**LOD Group** remains the explicit tool. Dithered cross-fade works with the Resident Drawer; animated cross-fade did not, and Unity's fix excludes such groups from instancing (issue UUM-91634).

**Small-mesh culling** is a URP setting ("Small-Mesh Screen-Percentage") that culls objects below a share of the screen. Ours is 0.

**HLOD** does not exist in Unity. It is "under consideration" on the roadmap; Unity's own HLODSystem repository was tested on 2021.3. Unreal's World Partition names the kinds we need: an instancing layer (each mesh at its lowest level), a merged mesh, a simplified mesh and an approximated mesh, with materials baked for the merged kinds.

**Simplification tools.** meshoptimizer (MIT) has `meshopt_simplify` with border locking (`meshopt_SimplifyLockBorder`), so chunks simplified apart do not crack. `meshopt_simplifyWithAttributes` weighs each attribute and can lock vertices. It also has a sloppy mode, pruning of small islands, `meshopt_analyzeCoverage` to measure how a silhouette changed, and clusters of 64 vertices and 126 triangles for Nanite-like work. Its `gltfpack` tool simplifies a glTF from the command line. Blender's own Decimate is already in our pipeline but weighs no attributes.

**Impostors.** Octahedral impostors (Ryan Brucks, for Fortnite) store a model from many directions with depth. Amplify Impostors is paid; URPIMP is a URP port of the CC0 IMP baker; an MIT octahedral implementation exists for Godot. One Unity user turned 3,000 plants into impostors and cut triangles from 1.7 million to 375,000, yet frame time went from 6.4 to 7.3 ms on a GTX 1060 (secondary). Impostors trade triangles for fill and texture memory, and they must be rebaked when the thing changes; for us that is about once an era.

### How dense worlds are drawn

**GTA V** (Courrèges' frame study, PC). 4,155 draws a frame: about 1,900 for the G-buffer, about 1,000 for four shadow cascades packed in one 1024×4096 texture, 650 to redraw the scene into a 240×120 water reflection. A compute shader picks each object's level by distance or culls it. Level changes are hidden by dithered stippling. Far off, "some really vast portions of the world are rendered in a single draw call": Vinewood Hills, dozens of houses, is "a single draw-call pushing only 2500 triangles", and Little Seoul is one draw. Distant lights are 32×32 quads. Streaming sets the camera's speed: planes are slowed and drawn at lower detail so loading keeps up.

**Assassin's Creed Unity** (Haar and Aaltonen, SIGGRAPH 2015). Paris was built modularly, "partially automated", with about ten times the instances of earlier games. Every mesh is cut into fixed 64-vertex clusters, culled on the GPU against the frustum, an occlusion depth pyramid and backfaces, and drawn with multi-draw indirect. Results: one to two orders of magnitude fewer draw calls, CPU at about 75% of the previous game with ten times the objects. On the GPU, 20 to 40% of triangles were culled but the gain was "<10% of geometry rendering"; 30 to 80% of shadow triangles were culled. Occlusion uses the 300 best occluders (about 0.6 ms), a 512×256 depth hierarchy and last frame's depth. The lesson for us: culling finer pieces helps shadows most, and culling alone does not rescue a scene whose visible triangles are too small.

**Marvel's Spider-Man** (Insomniac, GDC 2019). Manhattan had to fit on a Blu-ray and was marked up with procedural tools scoped so artists could refine their output by hand. For the second game, about twice as large, hand-made distant levels were "no longer viable" and became automated from mesh analysis (secondary; a GDC 2024 session page).

**Cities: Skylines 1** (Paradox wiki). The game builds a low-detail mesh for every asset on import and bakes the full model's textures and normals onto it. Suggested limits: 100 triangles for an ordinary building's far mesh, 200 for large ones, under 50 for props, 128×128 textures in a shared atlas, trees as billboards. "The effect of the LOD model on runtime performance is often more significant than the high detail version."

**Cities: Skylines 2 at launch** (Huhtala). A frame of 87.8 ms in RenderDoc: shadows about 40 ms and 4,828 of 6,705 draws (72%); four 2048 cascades; every object a shadow caster at every setting. Characters without levels: thirteen sets of teeth at 6,108 vertices each drawn for no visible pixel. A pile of logs over 100,000 vertices, drawn only in the shadow pass. Only frustum culling. About 121 million input vertices a frame. It runs on Unity (HDRP and DOTS). It is the cautionary tale this page is written against.

**Red Dead Redemption 2** (a third-party frame study). Footprints of people and horses are drawn into a 2048×2048 16-bit mud map that drives parallax occlusion mapping on the terrain: history kept in a texture, not in geometry. Most static point lights use baked shadow cubemaps; real-time shadow maps are made only near the player.

**Cyberpunk 2077 and Mafia: Definitive Edition** (engineers' frame captures). Cyberpunk draws instanced geometry with bindless textures, uses mesh decals that draw only the triangles carrying decal texture, and spreads shadow-map updates over several frames. Mafia lays its biggest occluders into the depth prepass in the first 120 draws.

**The Order: 1886** (SIGGRAPH 2013 notes and 2015 talk). Environment surfaces "relied on 90-95% tiling materials, with up to 4 runtime material layers authored using vertex blending, in conjunction with height maps"; decal projectors for damage and puddles; "a tiered system of beveling techniques by distance"; runtime instancing that "supported any number of blending variants per instance". Material layers were composited offline into parameter maps, from masks that could be generated (a cavity map baked from the sculpt drives dirt). Runtime layering blended mortar and wetness onto a tiling brick. Specular aliasing was fixed by folding the variance of the normal map under each texel into its roughness, per mip.

**Firewatch** (Jane Ng, GDC 2016, in Unity). Twenty-three trees made by hand, fourteen used everywhere. Pine C's levels at the PC's medium setting: 2,484, 1,461, 1,117, 739 and 4 triangles; the step from the second level to the third mostly drops shadow-casting geometry. Terrain shadow casting was turned off for cheap proxy casters underneath. Wind response is painted into vertex colour (red sway, green branch, blue leaf flutter). The world streams in sectors, and the same sectors swap the burned and the green forest by story day. Ng's rule: "It is better to have 10 really well made models that you can duplicate 20 times in varied ways, than 200 unique assets".

### What follows for us

- Long things must be cut into chunks. A flight, a wall or a street drawn as one mesh gets one level for its whole length, one bounding sphere and one shadow caster. AC Unity cut everything into 64-vertex clusters; we can cut at piece boundaries every few metres, where nothing can crack.
- The far town is its own baked object, made from the same parts by the generator: GTA's districts, Cities: Skylines 1's 100-triangle buildings with 128² baked textures, Spider-Man 2's automated far levels.
- Shadows get their own cheap geometry (Firewatch's proxies, Cities: Skylines 2's failure without them).
- Two regimes need separate budgets. In a lane at eye level, occlusion does most of the work (AC Unity's occluders, Mafia's prepass). From the close stop with the horizon in frame, and from the far stop looking down, little is hidden: district levels and shadows decide the frame.

## 2. Many small pieces

Stones, setts, slates, tiles, bricks and planks can be drawn five ways.

| Way | Wins where | Costs | Examples |
| --- | --- | --- | --- |
| Unique pieces merged into a chunk | pieces fitted to one place (stair treads, copings, a quay's capstones); close views | memory and disk scale with area; per-vertex history works as now | our stairs today |
| A library of approved pieces placed as instances | pieces that repeat by the thousand at similar sizes (setts, wall stones, slates, tiles, bricks, planks) | per-place history must come from instance data and world fields; repeats must not show | AC Unity's modular Paris; the Matrix City Sample, each building "made up of hundreds of instances"; Firewatch's rule |
| Textures with relief (normal maps, parallax occlusion, silhouette parallax) | the middle distance on large flat fields: paving, roofs, wall faces | shimmer and "swimming" at grazing angles; flat silhouettes unless silhouette-aware | Tatarchuk's cobblestone sidewalk (2006); CryEngine's guidance (secondary); RDR2's mud |
| Tessellation or displacement | large fields where the silhouette matters | GPU cost; Crimson Desert's paving shows shimmer and halo outlines behind objects (PC Games Hardware's test) | Crimson Desert (displacement plus parallax; the "silhouette POM" reading is unconfirmed) |
| Shader-built patterns | any pattern whose layout can be computed at a point: brick bonds, slate courses | the pattern must match the real pieces near by | trim sheets and layered materials (The Order, Insomniac's Ultimate Trim) |

No source we found drew setts, roof tiles or bricks as geometry at a distance, and none published triangle counts per piece per level. The masters agree on geometry at edges and silhouettes: a wall's top line, a roof's ridge, verge and first and last courses, corners. Behind them sits a cheaper body, and detail moves into textures and roughness as it leaves the geometry. The Order bevelled by distance; an environment artist's Assassin's Creed-style scene puts mesh bricks only at the corners of a tiling brick wall; the Matrix City Sample builds custom roofs only for odd shapes.

Three ideas make that work for us without breaking the rule that visuals may not claim what the facts do not say.

**The same stones at every tier.** A generic tiling sett texture at 30 m would show a joint pattern that is not the lane's. Instead, each chunk's street and city levels carry maps baked from its own near pieces: which piece covers each texel, its height for relief, its joints, its history. The street level of a flight draws the flight's own slabs, with their own lichen fields, as texture over simplified shapes. This is Cities: Skylines 1's bake from the full model to the far mesh, applied to every kind.

**Intrinsic and extrinsic history.** `stone.py` computes every channel per vertex in one place. Split them by cause. Intrinsic channels depend only on the piece's own shape: which face a point is on (`kind`), its distance to an edge, what of the sky the piece's own form hides. They can live in a shared library mesh. Extrinsic channels depend on the place: years since laid or bared, footfall and wear, water, damp, care. They come from per-instance data (a Renderer Shader User Value or a BRG buffer) and from field textures over the chunk. With that split, a sett from a library of fifty can sit in any lane and still carry that lane's years. Stair treads and copings, fitted to one place, keep both kinds per vertex.

**Layouts that can be evaluated at a point.** A slate roof's courses (each course a fixed gauge, each slate's width and tilt from a hash of its course and index) can be computed in a shader for any point. Then the street and city tiers can draw exactly the slates the near tier placed, with no bake at all. Rubble walls and stair slabs cannot be written that way and are baked. Setts can be, if the rule that a joint keeps off the joints of the row below is written per row from a hash rather than by walking the row. Where the craft allows, a layout that can be evaluated at a point is worth more than one that has to be walked.

## 3. Vegetation and nature at scale

**Ghost of Tsushima** (Eric Wohllaib's GDC 2021 talk; details from a write-up, secondary). A compute pass places blades on a jittered grid per tile, reads the terrain for grass type and height, culls and writes instance data. Blades are drawn with no vertex streams: each vertex is built from its index. A blade has 15 vertices near and 7 far, blended at the switch. Larger tiles drop three blades in four and widen the rest. Blades seen edge-on are thickened in view space. Voronoi clumps share height, colour and facing. One scrolling 2D noise drives the wind. Far off, the field becomes a texture on the terrain; grass shadows come from the terrain raised to grass height with dithered depth, plus screen-space shadows. AMD's open grass sample does the same with at most 32 blades a patch falling to 2, survivors widened by 32 over the count.

**Horizon Zero Dawn** (van Muijden, GDC 2017). Placement runs on the GPU around the player, data-driven, deterministic and locally stable: the same inputs give the same world, and a local edit does not reshuffle its neighbours. The slides report 500 or more asset types, over 100,000 objects in the scene and about 250 µs of average GPU time (secondary: read from a search excerpt of the slides).

**Firewatch** (above). Alpha cutoff lowered with distance, so far trees read puffier and more painted; proxies for shadows; wind in vertex colour; 23 trees.

**The Witness** (Ignacio Castaño). Alpha-tested foliage thins with distance because each smaller mip has fewer texels above the cutoff. The fix scales each mip's alpha so its coverage matches the first. Unity's importer has this as `mipMapsPreserveCoverage`, and our `ArtImport.cs` already sets it for the birches' sprays.

**Alan Wake 2** (Remedy). A scattering tool for mass-authoring vegetation; GPU skinning of every visible plant, "almost 300,000 bones in Cauldron Lake being processed every frame"; mesh shaders, meshlet culling and occlusion "down to a single-pixel precision". No level counts were published.

**Unity's terrain details** are GPU-instanced in URP, but colour variation is dropped when instanced and the system knows nothing of our fields. Unity's SpeedTree trees usually carry three or four materials, so several draws each. Neither fits a town where grass grows from the water, feet and sky fields.

What follows for our nature:

- Our near birch at about 60,000 triangles is 24 times Firewatch's pine at its first level. That is fine within 20 m, where scenes play; the street level (about 10,000), the city level (about 1,500) and an impostor past about 200 m must exist before trees are placed by the dozen.
- Few archetypes, many seeded placements. Firewatch's 23 trees and Ng's rule point the same way as our parts rule. A grown tree can stay unique near the camera; far off, a few dozen impostors per species, age and season, scaled and tinted per tree, claim only its size, shape class and season.
- Grass, heath and ground cover are placed on the GPU from the same fields the growth layer reads, thinned with distance while survivors widen, handed to the ground's colour past about 30 to 50 m. They are never GameObjects. In Unity that is a compute pass and `Graphics.RenderPrimitivesIndexedIndirect`, or BRG.
- Painterly distance is a dial for cost too: fewer, larger shapes far off (lower alpha cutoff, broader cards, normals blended to the mass) are cheaper and read more like paint.

## 4. Texture budgets

**The arithmetic.** A block-compressed texel costs about a byte at BC7 or half a byte at BC1, plus a third for mips. A 2048² BC7 map is about 5.6 MB with its mips. Our grain maps are 2048² at a metre a tile, so 0.5 mm a texel: right for 1 m and generous beyond, and mips handle that. Tiled detail is cheap. What costs memory is anything unique per place.

**Unique bakes.** The street level needs about a texel per pixel at its near edge: 1 cm at 20 m. A metre of wall face 1.5 m tall at 1 cm a texel is 15,000 texels. With history packed into two compressed maps at about 2 bytes a texel in all, that is about 30 KB a metre, or 30 MB a kilometre on disk (estimate). Only what lies within the street tier's 80 m need be resident: perhaps a kilometre of wall and a few thousand square metres of paving at a busy street stop, tens of megabytes. The city level uses the same maps' smaller mips.

**Arrays, atlases and trims.** One material per family (stone, timber, render) with its pigments and grains in `Texture2DArray`s, indexed by a per-vertex or per-instance kind, keeps the SRP Batcher and the Resident Drawer batching. Trim sheets (Insomniac's Ultimate Trim) belong to the materials study.

**Virtual texturing is not ours to use.** Unity's Streaming Virtual Texturing is HDRP-only and experimental. Far Cry 4's adaptive virtual textures drew terrain and a very large number of decals at 10 texels a centimetre over a 10 by 10 km world, and Unreal's runtime virtual textures cache layered materials and blend meshes into terrain. Both cache an expensive layered result and reuse it for hundreds of frames. Our world changes only when its history changes, by event and by decade, so we can do the caching offline per chunk and let mipmap streaming load what the camera needs. Unity's mipmap streaming loads levels per camera within a memory budget, falling back to smaller mips when the budget is full.

**How per-place variation is fed**, from cheapest to richest:

| Carrier | Good for | Limits |
| --- | --- | --- |
| World-space noise in the shader | texture that claims nothing (grain drift, a lean) | must never carry history; the same everywhere for the same position |
| Vertex data | unique merged pieces (stairs now) | memory per vertex; lost when a library mesh is instanced |
| Renderer Shader User Value | one GameObject's facts as an index into a buffer | 32 bits a renderer |
| BRG instance buffer | setts, slates, grass by the thousand | our own code; no GameObjects |
| Field textures | the feet, water, sky and care fields (`docs/living-fabric.md`) | resolution: a town-wide map at 5 cm is impossible, so fields come in tiles per chunk (a 64×64 tile for a 4 m chunk is 6 cm a texel and 16 KB), in an array indexed by chunk |
| Baked chunk maps | the street and city levels | rebaked when a fact changes |

## 5. History through levels and merges

**Bake inputs, not outputs.** Unreal's HLOD bakes material results into textures, and Simplygon can cast a material into vertex colours at the end of a level chain. Both freeze the light and the weather. Our shader draws history from causes: years, polish, lichen years, moss, water. If the bake keeps those inputs, the same `Stone.shader` draws the street and city levels through a texture path, and wetness, the hour and the season stay live at every distance. The Order's offline compositing is the precedent for baking the expensive part and leaving the cheap blend live.

**History as a function of position.** `put()` in `stone.py` already computes every channel from the piece's facts and a point on it. Pulled out as a pure function, `history(piece, point) -> channels`, it can be sampled at the close level's vertices, at a coarser level's vertices, or at the texels of a chunk's baked map, and all three agree because they sample one field. That removes the usual problem of keeping attributes alive through simplification: nothing is kept, everything is sampled again.

**One carrier per level:**

| Level | Shape | History carried by |
| --- | --- | --- |
| Close (to about 8 m) | every piece as now: chamfers, flakes, the worn hollow, joint fills, pointing | per vertex, as now; near marks in the shader (`OS_Near`) |
| Near (8 to 20 m) | each piece simplified from its own seed and outline: fewer outline points, a coarser top grid, no flakes; fills and pointing gone into the maps | per vertex, sampled again; joints from the maps |
| Street (20 to 80 m) | bevelled boxes for steps and copings, a ribbon with its top line for a wall, a grid for paving; silhouettes true | the chunk's baked maps: piece, height, joints and history channels |
| City (80 to 200 m) | merged per flight, wall or lane: a stepped ribbon, a battered ribbon | the same maps' mips |
| District (200 m on) | merged per block with the houses and the ground | a block atlas (Cities: Skylines 1's 128² per building, GTA's districts) |
| Far | terrain, impostors | baked colour |

Moving history from vertices to maps at the street level also halves the vertex: position, normal and two UVs (grain and map) instead of six channels.

**When relief leaves the geometry, keep it in the gloss.** A wet worn tread glitters because of its micro-relief. When the relief is gone, fold its variance into roughness in the bake, as The Order did for its normal maps, so a flight far off is as glossy in the rain as it is near.

**Hide the changes.** GTA V's dithered stippling hides its level changes; URP's dithered cross-fade does the same and works with the Resident Drawer. Our shaders need `LOD_FADE_CROSSFADE`. A dither suits a painted look better than a pop.

**Cache by hash.** `docs/living-fabric.md` already says a life is computed offline per thing, cached by a hash of its facts and the rules' version, and rebuilt only when a fact changes. The bakes join that cache: same hash, same maps.

## 6. Quality control at scale

### Visual regression

- **Unity, from the start** (Aras Pranckevičius, 2007 and 2011): one small scene per feature, run at a fixed timestep, a screenshot compared with a known good image per platform, a couple of wrong pixels allowed because "many consumer GPUs are not fully deterministic". Every failure leaves the expected image, the result and a contrast-boosted difference. Every regression found by hand becomes a new test.
- **URP's own tests today** (Unity's Graphics repository): 512×512 captures, an average threshold of 0.005 and a per-pixel threshold of 0.001 (deltaE), a higher floor of 0.002 on AMD cards, references kept per colour space, platform and graphics API. They run on Metal Mac minis, without `-nographics`.
- **Frostbite** (Jon Valdés, REAC 2024): eleven platforms, more than 1,000 test suites, 32,849 reference screenshots kept per platform and per GPU vendor, run before and after each submit. Each pixel is compared with NVIDIA's FLIP and an image scores its worst pixel, against "extremely stringent thresholds", because "a single bad pixel can be terrible", like the centre of the sun going black. Exact comparisons are "short-term pain, long-term bliss"; loose thresholds are the reverse. Texture filtering is the largest difference between vendors. Shader functions are unit-tested on WARP, a CPU renderer, to remove GPU differences.
- **Unreal and Chromium** keep ground truth per platform and graphics API, and make approving a new image a deliberate act that goes into source control. Chromium's Skia Gold triages results as positive, negative or untriaged; untriaged images keep the bots red.
- **Bart Wronski** (2019) argues for 10 to 15 golden smoke tests and property tests for the rest: no NaN, energy kept, values in range.
- **NVIDIA FLIP** produces a map of perceived difference per pixel and a mean; NVIDIA now recommends the mean over its earlier weighted median. The main version is for LDR images, which our graded frames are.

### Performance

- **Frostbite** runs performance tests regularly on its farm on CPU and GPU markers and alerts when results deviate from history in either direction, to stop slow drift.
- **Unity's Performance Testing package** samples frames after a warm-up (`Measure.Frames`); Unity's benchmarking advice is a fixed quality level, VSync off, and medians or percentiles rather than means.
- **FrameTimingManager** reports CPU and GPU frame time on Metal, four frames late, and warns that on tile-based GPUs such as Apple's "the reported GPU time might be larger than the reported frame time" under heavy load. M4 numbers are relative, not absolute.
- **ProfilerRecorder** reads the render counters in release players: draw calls, SetPass calls, batches, triangles, vertices, shadow casters.

### Asset checks

- Cities: Skylines 2 shipped props with no levels and every object casting shadows. Cities: Skylines 1 had limits per class. A budget per class and per level, checked at export, is the cheapest test there is.
- Unity's `AssetPostprocessor` is where import rules live (`ArtImport.cs` already raises its version when rules change, so assets re-import). Unity 6.4 and later build in Project Auditor, which runs headless and takes custom analysers; 6.6 adds a URP settings analyser.

### Variety and culture

- **Expressive range** (Smith and Whitehead, 2010): generate thousands of outputs, score each on two measures of what came out (not of the inputs), plot them as a 2D histogram, and look at samples from each cell. It showed their generator's bias towards linear levels.
- **Sea of Thieves** (Rare, GDC 2019) was built around automated testing from the start; Rare now also unit-tests its HLSL. Riot runs about 5,500 tests in about 18 minutes per build and lets a new test gate nothing until it has been stable for a week.
- The pattern across them: fast checks on every change, the full suite nightly, humans looking at sheets on a fixed rhythm, and every bug that escapes becoming a test.

## Our approach against this

### Stairs, walls and setts: what must change

1. **Chunks at piece boundaries.** A flight is written as runs of three to five metres, cut at a landing or between steps. A wall is written as panels of about four metres, cut at a joint between face stones. A lane is written as patches of about four by four metres. Each chunk is its own mesh with its own bounds, levels and shadow caster. Pieces are separate bodies, so a cut never cracks. A chunk is small enough for its bounding sphere to be occluded, and for the step at your feet to draw at the close level while the top of the flight draws at the near level.
2. **Levels made by the generator from the same seed.** Every part generator takes a level. `slab.py` makes the close level as now, brought within the foundations' 600 triangles a slab (a 1.4 m tread is 1,100 today). Its near level has about ten outline points, a 25 cm top grid and one ring a face, about 100 to 150 triangles. Its street level is a bevelled box of 12 to 24. `sett.py` goes from 72 to a crowned box of about 20, then to nothing but the map. `wallstone.py` goes from 70 to 130, to about 20, then to the map. Fills, pointing and soil strips exist only at the close level. The outline stays the seed's, so the shape never jumps.
3. **History as a pure function** (`history(piece, point)`), split into intrinsic and extrinsic channels, sampled at each level's vertices and at each bake's texels.
4. **Bakes for the street and city levels.** Per chunk, a map set baked from the close level: piece and joints, height for relief, the history channels, and the relief's variance folded into roughness. `Stone.shader` gains a texture path (a keyword) that reads the same channels from the maps. The street level's vertex shrinks from 72 bytes to about 40.
5. **Shadows by proxy.** The close and near levels never cast. Each chunk's street level casts within the first cascades and its city level beyond. Fills, pointing, setts and moss cushions never cast: their small shadows are the baked occlusion and the shader's.
6. **Libraries for repeated pieces.** Setts, wall face stones, roof slates and tiles, bricks and planks come from libraries of approved variants: a few dozen setts, a few hundred wall stones in size classes. Each is placed as an instance with its transform, its extrinsic facts and an index into the chunk's field tile. Close to the camera they are drawn through BRG; further off the chunk's maps take over. Whether a wall stone stretched by a few per cent to fit its course still reads true is a look test on the slab sheet before it is a rule. Stair treads, copings and other fitted pieces stay unique.
7. **Shaders ready for the Resident Drawer.** `Stone.shader`, `Street.shader` and `Tree.shader` move to `#pragma target 4.5` with `DOTS_INSTANCING_ON`, `LOD_FADE_CROSSFADE` and a read of `unity_RendererUserValue`.
8. **Generated meshes out of git.** Generators, facts and a manifest of mesh hashes are committed; meshes are rebuilt from them. A compact binary chunk format (positions quantised to 16 bits per chunk, normals octahedral, history in 8 bits a channel) comes when streaming does.

At the current density a kilometre of wall is about 5 million triangles and, as FBX, about 200 MB. With libraries and bakes it is about 50,000 instance records and 30 MB of maps (estimates). That difference decides whether London is possible.

### A tier plan per kind

Budgets are per unit, provisional, to be confirmed by the harness. "Close" and "near" are the two halves of the foundations' near tier; "city" and "district" the two halves of its city tier. Each level is chosen by its error in pixels; the distances are for the 35 mm lens at 1440p.

| Kind | Close (to 8 m) | Near (8 to 20 m) | Street (20 to 80 m) | City (80 to 200 m) | District and far | History carrier | Shadows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Stairs (per step, 3 m wide) | under 2,500 (now 3,400 to 5,900) | about 300 | about 30: two or three bevelled boxes | about 6: a stepped ribbon | part of the lane | vertices, then the chunk's maps | street level within the first cascades, city level beyond |
| Walls and kerbs (per metre) | under 4,000 (now about 5,000) | about 600 | about 60: a ribbon with its true top line and batter, copings as boxes | about 10 | part of the block | vertices or instances, then maps | as stairs |
| Paving, setts (per square metre) | about 3,500 as instances, only to about 8 m | the chunk grid with parallax from the height map, under 50 | under 4 | part of the lane surface, about 1 | terrain | instance data and field tiles, then maps | none for setts; kerbs as walls |
| Quays and quay steps | as walls and stairs | as walls | as walls | as walls | part of the shore | as walls | as walls |
| Natural stone (bedrock, ledges, boulders) | the generator's mesh, about 2,000 per square metre of face | simplified with locked chunk borders (meshoptimizer) | about 50 per square metre, relief in maps | merged into the land | the land | maps baked from the close mesh | street level |
| Buildings (per house) | 40,000 (foundations) | 40,000 | 8,000 | 1,500 | about 200 on a block atlas, then block silhouettes | per-house maps for coats and wear | city level as caster |
| Street things (lamp, post, railing, bench) | a lamp about 3,000 | 3,000 | about 500 | about 60, culled by screen size | culled | Renderer Shader User Value into the thing's record | street level; none past the city tier |
| Trees | 60,000 (scenes, eye level) | about 30,000 (proposed; `docs/research/trees.md` aims at 20,000 to 30,000 for the street stop) | 10,000 | 1,500 | octahedral impostors per species, age and season | instance data: season, hue, wind phase | proxy casters (Firewatch); none for impostors |
| Grass, heath, ground cover | GPU blades, full density | thinned, survivors widened | thinned to about 50 m | the ground's colour | the ground's colour | the fields (water, feet, sky) | none; screen-space contact shadows |
| Moss cushions, ferns in joints | geometry | geometry thinned | the growth layer's film | film | film | the growth channels | none |
| Land (terrain) | chunked mesh at about 0.5 m, ledges as natural stone | same | about 2 m | about 8 m | about 32 m and the far terrain's baked colour | field tiles, then a top-down map | coarse caster |
| Water (sea, Basin, streams) | a grid round the camera with shader waves; quay edges as walls | same | same | coarser | a plane | none | none |

The far stop (about 120 m, steep) shows one or two hectares at the city level. The close stop with the horizon in frame is the worst case: every level at once, and houses out to a kilometre or more. Without a district level that view would draw something like a thousand houses at 1,500 triangles each (estimate).

### The performance harness, to build now

1. **A runner in the game, not the editor.** Unity says rendering speeds up less in the editor's views than in a build. `Overstory.Perf.PerfRunner` (runtime code) loads a scene, plays a path, records and quits. `LT1Perf.Build` (editor, batch mode) builds a macOS player with "Frame Timing Stats" on. The player is launched from a logged-in session (rendering needs a GPU, so never `-nographics`) with `-screen-width 2560 -screen-height 1440` and our own arguments.
2. **Paths from the judging views.** Each path is a list of `CameraShot` keys and a frame count, advanced by frame number, not by time. Four paths to start:
   - eye level up the gully steps, 1.65 m above the treads;
   - the street stop gliding along the lane at 2.8 m;
   - the close stop at 12 to 15 m, turning a full circle with the horizon in frame;
   - the middle stop at 35 m and the far stop at 120 m, panning over the heart.

   Each path runs in the three judging lights. The 16:00 low sun with its long shadows is the costliest; the blue hour has the most lights. Wetness, the clock and the wind's time are fixed. A warm-up of a few seconds is thrown away. VSync is off and the quality level fixed.
3. **Recorded per frame.** FrameTimingManager gives the CPU main thread, render thread and GPU times. ProfilerRecorder gives draw calls, SetPass calls, batches, triangles, vertices and shadow casters. One screenshot is kept per segment.
4. **Written per run.** A CSV of every frame and a JSON summary per segment (median, 95th and 99th percentile, worst frame) go to `reviews/perf/<date>/`. A script beside `blender/tools/light_sheet.py` draws the sheet. It plots frame time along each path against the budget and against the last accepted run, and lays the segments over the heart's plan as a heat map.
5. **Switches for A/B runs.** The Resident Drawer and GPU occlusion, each on or off. MSAA 4× against no MSAA with depth priming. Shadow distance and cascades. LOD bias. A forced level per kind, to judge each level alone. The history path, vertices or maps.
6. **Gates.** A run worse than the last accepted run by more than its own noise, or over budget, is flagged. A run that is better is flagged too, so drift is seen both ways. Generators are deterministic, so `git bisect run` with the harness finds the commit.
7. **The reference machine.** The M4 is about a third to a half of an RTX 3060 (secondary). A tile-based GPU also behaves differently: overdraw of opaque surfaces and MSAA are cheap there, alpha testing and dense geometry are not. Until Øystein decides otherwise, the budget is set on the M4 itself at 1440p, and each change is judged against the last accepted run.

Cost: about three days. It turns every later decision on this page into a number.

### Visual regression and checks, to build now

1. **Golden views.** `LT1Golden` (editor, batch mode on the GPU) renders about a dozen fixed views. They are the corner from eye level, the street stop, 12 m and the far stop, in grey light and in the low sun, plus a stone sheet and a tree sheet. Each is rendered at 512×512 like URP's own tests, with 512² crops at full resolution where detail lives (a nosing at eye level, a lichen field). Antialiasing that varies frame to frame, motion blur and adaptive exposure are off; our exposure comes from the light and is fixed.
2. **The noise floor first.** Render every view twice on the same machine and measure the difference. Thresholds sit just above that floor, as strict as Frostbite's, and are tightened when they can be.
3. **Comparison.** A Python script compares each view with its baseline using FLIP (mean and worst pixel) and writes the baseline, the new image, an amplified difference and the FLIP map side by side into `reviews/regression/<date>/`, with one contact sheet for all.
4. **Only Øystein accepts a baseline.** The AI proposes; he accepts on the sheet; a script copies accepted images into `reviews/golden/baseline/`. An unaccepted difference blocks a merge to `main`. Baselines stay small (512² PNGs), so plain git holds them.
5. **Mesh hashes.** `blender/tools/mesh_hash.py` hashes every generated chunk (positions quantised to 0.1 mm, faces, history channels quantised) into a committed manifest, and the stress test compares. A change names the chunk it changed, with no GPU.
6. **Checks at export and import.** `validate.py` and `ArtImport.cs` check each chunk at each level:
   - triangles against the tier's budget, and each level at most about 60% of the one before;
   - the estimated median triangle at the level's nearest distance, ten pixels or more;
   - no degenerate or sliver triangles;
   - history channels present and in range;
   - one material per chunk;
   - shadow casting off on the close and near levels and on small parts;
   - bounds and pivots.

   Project Auditor runs headless with the URP analyser.
7. **Variety.** Each generator runs a few hundred seeds, scored on two measures of what came out: for a flight, steps against landings; for a wall, lichen cover against the share of reset panels. The scores are plotted as a 2D histogram, with a contact sheet drawn from each cell.
8. **Cadence.** On every commit: hashes, export checks, the smoke views at 512². Nightly: all golden views, the performance paths, the variety sheets. Weekly: Øystein looks at the regression sheet and the heat map. Each bug that escapes becomes a test.

Cost: about four days for golden views, FLIP sheets and the accept script; two for hashes and checks; one for variety plots.

## What we should do

Ranked by what each buys for its cost.

1. **Build the performance harness on the corner** (about three days). Buys frame time, triangles and draws for every judging view in three lights, before and after every change. Nothing below should be judged without it.
2. **Tick Mesh LOD on the gully's FBX and measure** (an afternoon). Buys a cheap baseline: how far plain simplification goes, and what it breaks (joints and history are expected to smear).
3. **Chunk the stone generators and give every part three levels** (four to six days, stairs and walls first, the lane's setts as they are built). Buys the corner within budget from eye level to the far stop; five to twenty times fewer triangles past 8 m; culling, levels and shadows per chunk. This is the "tiers" step `NOW.md` already names after the corner's stone review.
4. **Make history a pure function, split intrinsic from extrinsic** (two to three days, `stone.py` and `wall.py`). Buys exact history at every level, the bakes, and instanced libraries.
5. **Bake the street and city levels from the close level, and give `Stone.shader` its texture path** (five to eight days). Buys the same stones at every tier, half the vertex, live weather at every distance, and a town that fits in memory.
6. **Shadows by proxy** (a day, once chunks exist). Buys protection from Cities: Skylines 2's failure: the shadow passes stop redrawing every flake.
7. **Golden views, FLIP sheets and the accept script** (about four days). Buys certainty that a change changed only what it meant to, judged by Øystein.
8. **Mesh hashes, export and import checks** (about two days). Buys budgets and determinism checked on every commit, at no GPU cost.
9. **Generated meshes out of git** (a day). Buys a repository that survives the town (2.2 GB now, 36 MB per stair).
10. **Shaders ready for the Resident Drawer; turn it and GPU occlusion on under the harness** (one to two days). Buys CPU headroom for kit parts, street things and trees, and per-thing facts through Renderer Shader User Value.
11. **Libraries and BRG for repeated pieces** (four to six days, with the lane's paving and the houses' roofs). Buys paving and roofs at town scale in megabytes, not gigabytes.
12. **The trees' street and city levels and impostors** (about a week, with the trees' open list). Buys trees by the hundred.
13. **The district level: per-block merged proxies with atlases** (about a week, in plan step 6). Buys the close stop's horizon.
14. **GPU grass and ground cover from the fields** (about a week, in plan step 7). Buys the ground's living cover without GameObjects.

## Decisions for Øystein

1. **The reference machine and its target.** The M4 Mac mini is the only machine. Either the budget is set on it (for example 1440p at 30 frames a second, roughly a mid-range PC card at 60; unverified), or a PC with an RTX 3060-class card is borrowed now and then for a check.
2. **Libraries for repeated pieces.** Setts, wall stones, roof slates, tiles, bricks and planks drawn from libraries of judged variants placed with variation, rather than a unique stone everywhere (gigabytes on disk, or a second copy of every generator running inside Unity). This follows the project's rule that generators place approved parts.
3. **Generated meshes leave git.** Generators, facts and hashes are committed; meshes are rebuilt from them.
4. **Antialiasing, after the harness.** MSAA 4× is sharp but stops depth priming and costs memory bandwidth on a PC card; temporal antialiasing or STP is softer, may suit the painted look, and makes golden images harder. Decide on measured frames.

## Gaps

- Several primary sources could not be read. The Ghost of Tsushima grass talk is a members-only video, so its details come from a write-up. The Horizon Zero Dawn slides were too large to fetch, so their numbers come from a search excerpt. The Spider-Man talks are members only. Ryan Brucks' impostor article and the Amplify manual would not load. Nothing usable was found for Breath of the Wild, Far Cry 5, The Witcher 3, Kingdom Come: Deliverance 2, Hitman, Watch Dogs: Legion, A Plague Tale, Dishonored 2 or Disco Elysium. The session's shared search budget ran out before they could be tried again.
- No published triangle counts per cobble, tile or brick at each level were found. Our budgets come from the pixel arithmetic and must be confirmed in the harness and on the sheets.
- The M4 against an RTX 3060 rests on synthetic benchmarks; how our frames scale between them is not known.
- How Mesh LOD treats our six UV channels and sharp edges is undocumented; the afternoon's test answers it.
- `Stone.shader`'s cost per pixel, the Resident Drawer's gain on our content and GPU occlusion's gain in lanes are unmeasured.
- The memory figures for bakes and libraries are estimates.
- How fast the free camera may rise from a lane to the far stop before streaming shows (GTA V slowed its planes) is unknown until there is streaming.
- Whether a stretched library stone reads true at eye level is a look test, not yet run.

## Sources

Unity: [GPU Resident Drawer](https://docs.unity3d.com/6000.3/Documentation/Manual/urp/gpu-resident-drawer.html) · [Making objects compatible](https://docs.unity3d.com/6000.3/Documentation/Manual/urp/make-object-compatible-gpu-rendering.html) · [Resident Drawer performance](https://docs.unity3d.com/Manual/urp/gpu-resident-drawer-performance.html) · [DOTS instancing in custom shaders](https://docs.unity3d.com/Manual/dots-instancing-shaders-support.html) · [BRG and DOTS instancing](https://docs.unity3d.com/6000.3/Documentation/Manual/dots-instancing-shaders.html) · [Renderer Shader User Value](https://docs.unity3d.com/Manual/renderer-shader-user-value-intro.html) · [GPU occlusion culling](https://docs.unity3d.com/6000.3/Documentation/Manual/urp/gpu-culling.html) · [Mesh LOD](https://docs.unity3d.com/6000.3/Documentation/Manual/lod/mesh-lod-introduction.html) · [Mesh LOD generator](https://docs.unity3d.com/6000.3/Documentation/Manual/lod/mesh-lod-generator.html) · [Animated cross-fade with the Resident Drawer (UUM-91634)](https://issuetracker.unity3d.com/issues/animated-cross-fade-on-lodgroups-doesnt-work-with-gpu-resident-drawer) · [Cross-fade forum thread](https://discussions.unity.com/t/lod-crossfade-in-graphics-resident-drawer/1561993) · [URP asset](https://docs.unity3d.com/6000.3/Documentation/Manual/urp/universalrp-asset.html) · [Universal Renderer, depth priming and MSAA](https://docs.unity3d.com/6/Documentation/Manual/urp/urp-universal-renderer.html) · [New in 6.6](https://docs.unity3d.com/6000.6/Documentation/Manual/WhatsNewUnity66.html) · [New in 6.4](https://docs.unity3d.com/6000.6/Documentation/Manual/WhatsNewUnity64.html) · [Resident Drawer performance thread](https://discussions.unity.com/t/resident-drawer-performance/1554861) · [HLOD on the roadmap](https://activation.unity3d.com/roadmap/1879-hierarchical-level-of-details-generation) · [HLODSystem](https://github.com/Unity-Technologies/HLODSystem) · [Streaming Virtual Texturing](https://docs.unity3d.com/Manual/svt-requirements-compatibility.html) · [Mipmap streaming](https://docs.unity3d.com/Manual/TextureStreaming-introduction.html) · [mipMapsPreserveCoverage](https://docs.unity3d.com/ScriptReference/TextureImporter-mipMapsPreserveCoverage.html) · [Terrain grass](https://docs.unity.com/en-us/engine/6000.3/manual/creating-environments/script-terrain/terrain-grass) · [SpeedTree in Unity](https://docs.unity3d.com/6000.0/Documentation/Manual/SpeedTree.html) · [FrameTimingManager](https://docs.unity3d.com/6000.3/Documentation/Manual/frame-timing-manager.html) · [Rendering profiler counters](https://docs.unity3d.com/Manual/ProfilerRendering.html) · [Measure.Frames](https://docs.unity3d.com/Packages/com.unity.test-framework.performance@3.0/manual/measure-frames.html) · [Benchmarking in Unity](https://unity.com/blog/engine-platform/performance-benchmarking-in-unity-how-to-get-started) · [Graphics Test Framework](https://docs.unity3d.com/Packages/com.unity.testframework.graphics@8.9/manual/index.html) · [URP graphics test settings](https://github.com/Unity-Technologies/Graphics/blob/master/Tests/SRPTests/Packages/com.unity.testing.urp/Scripts/Runtime/UniversalGraphicsTestSettings.cs) · [Project Auditor](https://docs.unity3d.com/Manual/project-auditor/project-auditor-introduction.html) · [Megacity 2019](https://github.com/Unity-Technologies/Megacity-2019)

Games and engines: [GTA V graphics study](https://www.adriancourreges.com/blog/2015/11/02/gta-v-graphics-study/) and [part 2](https://www.adriancourreges.com/blog/2015/11/02/gta-v-graphics-study-part-2/) · [GPU-driven rendering pipelines, AC Unity and RedLynx, SIGGRAPH 2015](https://advances.realtimerendering.com/s2015/aaltonenhaar_siggraph2015_combined_final_footer_220dpi.pdf) · [Spider-Man technical postmortem, GDC 2019](https://gdcvault.com/play/1026496) · [Automating distant city LODs in Spider-Man 2](https://schedule.gdconf.com/session/applied-mesh-analysis-automating-distant-city-lods-in-marvels-spider-man-2/899260) (secondary) · [Cities: Skylines asset editor](https://skylines.paradoxwikis.com/Asset_Editor) · [Cities: Skylines 2 performance](https://blog.paavo.me/cities-skylines-2-performance/) · [RDR2 graphics study](https://imgeself.github.io/posts/2020-06-19-graphics-study-rdr2/) · [Cyberpunk 2077 rendering analysis](https://zhangdoa.com/rendering-analysis-cyberpunk-2077) · [The rendering of Mafia: Definitive Edition](https://www.elopezr.com/the-rendering-of-mafia-definitive-edition/) · [The Order: 1886 material pipeline, SIGGRAPH 2013](https://blog.selfshadow.com/publications/s2013-shading-course/rad/s2013_pbs_rad_notes.pdf) · [Crafting Victorian London, SIGGRAPH 2015](https://history.siggraph.org/wp-content/uploads/2022/10/2015-Talks-Phail-Liff_Crafting-Victorian-London-The-Environment-Art-and-Material-Pipelines-of-The-Order-1886.pdf) · [Making the World of Firewatch, GDC 2016](https://media.gdcvault.com/gdc2016/Presentations/Ng_Jane_MakingTheWorld.pdf) · [Procedural grass in Ghost of Tsushima, GDC 2021](https://gdcvault.com/play/1027214/Advanced-Graphics-Summit-Procedural-Grass) and [a write-up](https://tigerabrodi.blog/grass-in-ghost-of-tsushima) (secondary) · [GPU-based procedural placement in Horizon Zero Dawn](https://www.guerrilla-games.com/media/News/Files/GDC2017_VanMuijden_GPUBasedProceduralPlacementInHorizonZeroDawn.pdf) · [AMD procedural grass with mesh shaders](https://gpuopen.com/learn/mesh_shaders/mesh_shaders-procedural_grass_rendering/) · [Alan Wake 2's Northlight](https://www.remedygames.com/article/how-northlight-makes-alan-wake-2-shine) · [Computing alpha mipmaps (Castaño)](https://www.ludicon.com/castano/blog/2010/09/computing-alpha-mipmaps/) · [Crimson Desert technical test, PC Games Hardware](https://www.pcgameshardware.de/Crimson-Desert-Spiel-72378/Tests/Release-Review-Steam-Performance-DLSS-4-5-FSR-4-1521842/4/) · [Crimson Desert surfaces](https://shazoo.ru/2026/04/15/182427/razrabotciki-iutuber-sdelal-razbor-togo-kak-crimson-desert-sozdaet-realisticnye-poverxnosti-sten-i-zemli-bez-poteri-proizvoditelnosti) (secondary) · [Parallax occlusion mapping (Tatarchuk)](https://advances.realtimerendering.com/s2006/Chapter5-Parallax_Occlusion_Mapping_for_detailed_surface_rendering.pdf) · [CryEngine POM](https://cryengine.com/docs/static/engines/cryengine-3/categories/1114113/pages/1048721) (secondary) · [Adaptive virtual textures in Far Cry 4](https://gdcvault.com/play/1021760/Adaptive-Virtual-Texture-Rendering-in) · [Unreal World Partition HLOD](https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition---hierarchical-level-of-detail-in-unreal-engine) · [Unreal runtime virtual texturing](https://dev.epicgames.com/documentation/en-us/unreal-engine/runtime-virtual-texturing-in-unreal-engine) · [City Sample](https://dev.epicgames.com/documentation/en-us/unreal-engine/city-sample-project-unreal-engine-demonstration) · [Simplygon vertex colour casting](https://simplygon.com/features/vertexcolorcasting) · [The Ultimate Trim](https://gdcvault.com/play/1022323/The-Ultimate-Trim-Texturing-Techniques) · [Assassin's Creed-style modular scene](https://80.lv/articles/building-assassin-s-creed-odyssey-modular-scene-with-ue-3d-designer/) · [meshoptimizer](https://github.com/zeux/meshoptimizer) · [Nanite, a deep dive](https://advances.realtimerendering.com/s2021/Karis_Nanite_SIGGRAPH_Advances_2021_final.pdf) · [Overdraw in overdrive (Self Shadow)](https://blog.selfshadow.com/publications/overdraw-in-overdrive/) · [Quad-fragment merging (Fatahalian et al.)](https://www.microsoft.com/en-us/research/?p=159994) (secondary) · [Android geometry guidance](https://developer.android.com/games/optimize/geometry) · [Amplify Impostors thread](https://discussions.unity.com/t/amplify-impostors-next-generation-billboards/707589) (secondary) · [URPIMP](https://github.com/hickVieira/URPIMP) · [RTX 3060 against the M4](https://nanoreview.net/ru/gpu-compare/geforce-rtx-3060-vs-apple-m4-gpu-10-core) (secondary)

Quality control: [Testing graphics code (Aras, 2007)](https://aras-p.info/blog/2007/07/31/testing-graphics-code/) · [Four years later (2011)](https://aras-p.info/blog/2011/06/17/testing-graphics-code-4-years-later/) · [Testing rendering code at Frostbite, REAC 2024](https://enginearchitecture.org/downloads/Testing_Rendering_Code_at_Frostbite-REAC.pdf) · [Unreal screenshot comparison](https://dev.epicgames.com/documentation/unreal-engine/screenshot-comparison-tool-in-unreal-engine) · [Chromium pixel tests with Gold](https://chromium.googlesource.com/chromium/src/+/HEAD/docs/gpu/gpu_pixel_testing_with_gold.md) · [How (not) to test graphics algorithms (Wronski)](https://bartwronski.com/2019/08/14/how-not-to-test-graphics-algorithms/) · [FLIP](https://research.nvidia.com/publication/flip) and [its code](https://github.com/NVlabs/flip) · [Smith and Whitehead 2010](https://users.soe.ucsc.edu/~ejw/papers/smith-pcg-2010.pdf) · [Automated testing in Sea of Thieves, GDC 2019](https://gdcvault.com/play/1026366/Automated-Testing-of-Gameplay-Features) · [Automated testing of shader code (Rare)](https://learn.microsoft.com/en-us/shows/pure-virtual-cpp-2024/automated-testing-of-shader-code) · [Automated testing for League of Legends](https://www.riotgames.com/en/news/automated-testing-league-legends) · [GitHub and large files](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)
