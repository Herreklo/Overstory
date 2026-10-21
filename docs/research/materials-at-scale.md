# Materials at scale

How the best studios and artists build materials and surface history for large worlds, and how they keep a painted read at every distance, set against how we build now. Part of a set of four studies: modular kits and generation (`docs/research/kits-and-generation.md`), performance and quality control (`docs/research/performance-at-scale.md`) and history in things (`docs/research/history-in-things.md`) sit beside it. This one is about how materials are built and layered: what lives in textures, in vertex data and in procedural shaders; layered and blended materials; trim sheets; tiling without repetition; decals; and how history survives distance. Claims taken from a summary are marked (secondary); claims we could not confirm are marked (unverified). Many talks sit behind GDC Vault's login; where only the abstract opened, we say so.

## In short

1. **Big worlds keep material identity in a small shared library.** Per-asset work goes into masks and parameters. Cyberpunk 2077 blends up to 20 library surfaces per mesh through masks; Unreal's material layers, the material banks of Hitman and Assassin's Creed, and Fallout 4's material swaps are the same idea. Our difference is a strength: our masks come from facts and geometry, never from an artist's brush.
2. **Detail is split by frequency.** Low-frequency "where" (wet, worn, mossy, peeled) lives in vertex colours, world masks or small maps. Mid-frequency identity (grain, boards, tiles) lives in tiling painted textures. High-frequency "how" (the crust's edge, the crack, the flake) comes from height maps and noise thresholded against the field. Tiny Glade drives its plaster damage from one float per vertex: the distance to the window.
3. **Our stone spends its triangles where they read, but cannot shed them with distance.** The gully's two flights carry 98,000 and 263,000 triangles, over half of them on the split faces, whose plates stand 1.2 to 2.2 cm proud and read from the street stop. Decimated to a third, flight 0 keeps 95 percent of its surface within 2 mm, under half a pixel from the street stop (measured). It cannot be decimated today, because its history rides on its vertices.
4. **Houses cannot carry history per vertex at all.** A lapped board is a long strip of a few triangles; a drip under a sill or a flake of paint is centimetres wide. The coat stack, the ghost sign and the drip need texture space. This is the one change that must come before plan step 2.
5. **Painterly games keep their read with value, air and medium-sized shapes.** They fade things in and never pop them. Sable's fog and fading lines, Firewatch's detail rationed to what matters, Dishonored 2's rule against fine noise, and Ghost of Tsushima's light and grading all put the image in light and large shapes. History survives distance the same way: the same fields at every tier, each mark resolving into its painted shape and then its mean, never vanishing.

## 1. How the best build materials at scale

### A library of surfaces, and masks per asset

**Cyberpunk 2077's multilayered shader.** CD Projekt Red's "supershader" builds most hard surfaces from three kinds of file (redmodding wiki, community documentation, secondary):

| File | What it holds |
| --- | --- |
| `.mlmask` | up to 20 mask textures, hand-authored for each mesh |
| `.mlsetup` | each layer's settings: tiling, colour and more, and which surface it uses |
| `.mltemplate` | the library's surfaces (steel, iron, aluminium, plastic, concrete, soil and more), each with colour, normal, roughness and metal textures |

CDPR's own artists confirm the shape of it: a multi-layer shader system, a material library built in Substance Designer and edited in an in-house Material Library Manager, and a bridge from REDengine to Substance Painter (80.lv interview). The point for us: a surface is made once and reused on every mesh, and an asset's identity is its masks and parameters.

**Unreal's material layers** formalise the same split in an engine: layer assets (a surface) and blend assets (a mask graph) stacked in a material instance, each layer's parameters exposed on the instance, so artists swap and reorder layers without touching the base material (Epic documentation).

**Material banks at Ubisoft, IO Interactive and Naughty Dog.** Assassin's Creed Odyssey's architecture materials were built from scratch in Substance Designer and layered in Painter from an in-house material bank (Vincent Dérozier's breakdown; the GDC 2019 talk itself is behind login). On Valhalla, vertex paint blends two texture sets in one material, for variety from fewer textures; materials are built in four detail layers (big shapes, medium shapes, small details, micro surface), and the Keep's few modules are varied with module changes, decals and colour (Tsvetelina Valkanova, 80.lv). IO Interactive's GDC 2021 talk describes a range of base materials made in Designer and applied in Painter to keep quality consistent and time low (Morten Olsen; abstract only). Naughty Dog moved to Substance Designer from The Last of Us into Uncharted 4 to feed a physically based pipeline with "vast amounts of content" while keeping a handcrafted look (Mosesian and Olguin, GamesBeat).

**Fallout 4's material swaps.** One mesh, several material files: a swap maps each material the mesh references to a replacement, so a clean pre-war object and its ruined post-war twin share geometry, and a script can apply a swap at runtime (Creation Kit wiki). It is the plainest form of history as material: the same thing, a different state.

**What it means for us.** Our shared surface layers (`docs/foundations.md`) are already a layer stack, and our materials (slate, granite, rubble, cement, soil) already share one shader and one set of includes. What we lack is the library as data: today a material's identity is spread across a Python dict (`STONES` in `stone.py`), shader properties on a saved material, a numpy painter and the shared packs. Section 5 proposes one record per material.

### Blending: vertex, world and height

**Vertex colour as the "where".** Naughty Dog's environment artists paint layers in with vertex colour. On The Last of Us Part I a texture artist describes each RGB channel painting its own layer: cracks, moss and wetness on walls (Jonathan Benainous's portfolio, secondary: the page would not open for us). A Naughty Dog texture artist on Uncharted 3 described blending two texture sets by their height maps, with a third (sand) filling cracks by slope (Polycount, secondary). Uncharted 4's technical artists gave moss shading and wetness shading their own features (SIGGRAPH 2016 talk abstract; the 13 MB slides were too large to open). The two secondary accounts come from different artists on different games and agree; the official abstract confirms moss and wet as shading features but not how they are masked.

**World masks.** On The Division, roads and pavements were painted into a world-spanning mask with three channels (snow, wetness, imprint); painting snow and wet together gave slush, and footprints over both made it icy. Marks that needed more resolution than the mask (ice puddles, drag marks, tyre tracks) were separate objects, and the artists left areas calm on purpose so the eye could rest (80.lv). Sucker Punch's tools for Ghost of Tsushima let artists write "texture and placement rules" in a bytecode-interpreted GPU language over generated data (Pohlmann, GDC 2021 abstract): rules as data, run over fields.

**A distance field per vertex.** Tiny Glade's windows wear the plaster round them irregularly from "a single float vertex attribute" holding the signed distance to the windows (Anastasia Opara, quoted by 80.lv). A distance interpolates well across big triangles; the shader turns it into a ragged edge with noise. This is the best single trick for us: store smooth fields, draw crisp edges.

**Height blending.** Andrey Mishkinis's terrain splatting gives each layer a depth map and keeps whichever layer stands higher, so sand fills the cracks first and stone tops stay clean; a depth offset sets how wide the blend band is (gamedev.net). The same rule decides which coat of paint survives, where moss sits in a step's laminae and where cement shows in a joint.

**Wetness as an order of events.** Sébastien Lagarde's series on wet surfaces gives the numbers. Wet diffuse falls to about 30 percent of dry at full wetness, and gloss rises (up to 2.5 times, clamped). Where water stands, gloss goes to 1, specular to water's (about 0.02) and the normal flattens. Puddles come from a painted vertex mask, cracks and holes from the height map. When rain stops, the wet level drops first, holes drain next, puddles last; a depth map from the rain's direction keeps sheltered walls dry (Lagarde, "Water drop 2b"). Our `Water.hlsl` does most of this already and should take two things from it: the order of drying by water held, and rain exposure as a field.

### Smart materials are masks from the shape

Substance's "smart materials" are layers revealed by generators that read baked mesh maps. Metal edge wear needs position, curvature, ambient occlusion and world-space normal: curvature puts wear on edges, occlusion keeps crevices clean, and a wear level reveals it progressively, like a histogram scan (Adobe documentation). On Dishonored 2, Substance masks did dust and dirt well, but edge-wear masks came out noisy and were cleaned by hand, and scratches were drawn by hand or taken from a library (Yannick Gombart, 80.lv). Material artists who model ageing well build in the order a thing was made and lived: wood, then knots and cavities, then splinters and wear, then mud, then paint (The Rookies, secondary).

For us, a smart material is a layer that reads facts and shape-masks the generator already bakes: the water layer, the sky and ground bake, which face a vertex sits on, how far it is from an edge, how high above the ground. The wear level is years times use times one minus care. The hand-cleaning Dishonored needed is replaced by rules about cause: wear only where contact puts it (`docs/stone.md`, Our style).

### Trim sheets

Insomniac's "Ultimate Trim" for Sunset Overdrive used a standard trim layout and normal-map structure, a UV script and a custom shader for variation. The talk's abstract says it let a small team build a large open world while raising quality (Morten Olsen, GDC 2015). Community write-ups describe the layout: strips in a fixed order and 45-degree bevels baked along every edge, so materials swap between assets without touching UVs (secondary). Blizzard's Fanny Vergne paints full trims by hand for World of Warcraft and keeps texture values neutral so lighting carries the mood (80.lv).

Our parts have real chamfers, so we do not need bevels in normal maps. What we need from trims is their economy: one painted atlas of strips (board faces, moulding faces, frame faces), mapped by the generator along each linear part with a seeded strip and offset, shared by every colour and era because the paint is the shader's.

### Tiling without repetition

Our stone hides tiling the way Inigo Quilez's first technique does: each piece samples the grain at its own offset and turn, and the joints hide the seams. Quilez's article gives two more: blending nine randomly offset, scaled and rotated copies by smooth Voronoi weights (nine fetches), and choosing between eight offset versions with a smooth low-frequency index, blending the two nearest (two fetches) (iquilezles.org). Heitz and Neyret's by-example noise blends randomly offset hexagonal tiles and keeps contrast with a histogram transform that must be precomputed. Morten Mikkelsen's hex-tiling at Unity drops the transform and samples the original texture, applying a contrast function to the blend weights instead. He stresses normal maps, since noise without repeats is ideal for surface detail (JCGT 2022). Unity's stochastic texturing prototype is not maintained (Unity blog).

Large continuous surfaces (render, asphalt, a lawn, a roof read as a field, the ground) have no joints to hide seams. They need hex-tiling or Quilez's index technique. On Valhalla, bark used unique textures for distance blended softly into tiling textures near, with a custom shader keeping the texel ratio constant across the switch, which the artist called the trickiest part (80.lv). Dishonored 2 avoided visible grid joints and rejected tiles with large uniform joints (80.lv). Our rule already says it: a brush mark has a size in the world and never tiles visibly.

### Decals

**Mesh decals** are geometry laid over a surface with their own material: a strip of rust, a poster, a painted sign. They break up reused, tiling assets cheaply and move like objects (Foundry Modo documentation; Polycount on Star Citizen's use of chamfered mid-poly models with decals, secondary). **Clustered decals** in DOOM (2016) are applied while each mesh is drawn, from an atlas, up to 256 decals a cluster beside its lights (Adrian Courrèges's frame study, secondary). **Unity's URP Decal Projector** in its DBuffer mode overlays albedo, normal, metal, smoothness and occlusion during opaque rendering, but needs a depth-normal prepass, skips OpenGL and has a maximum draw distance; the screen-space mode avoids the prepass (Unity documentation).

The Division's rule is the one to keep: marks with their own cause (drag marks by crates, litter by bin bags) are placed where their cause is, and need more resolution than the field (80.lv).

### What the famous games show about history in surfaces

| Game or artist | How history gets onto the surface | Source |
| --- | --- | --- |
| Fallout 4 | the same mesh with a clean or ruined material set | Creation Kit wiki |
| The Last of Us Part I | vertex channels paint cracks, moss and wetness layers | Benainous (secondary) |
| Uncharted 4 | moss and wetness as shading features | Brinck and Maximov (abstract) |
| The Division | a world mask for snow, wet, imprint; drag marks by context | 80.lv |
| Tiny Glade | plaster wear from distance to windows | 80.lv |
| Dishonored 2 | dirt uneven, noisy here and calm there; medium-scale detail | Gombart, 80.lv |
| Sea of Thieves | photo reference simplified by hand; things look used, with wear and makeshift repairs; shapes wonky but realistically so | notes on Rare's GDC 2018 talk (Habrador, secondary) |
| Assassin's Creed Valhalla | two texture sets blended by vertex paint; decals and colour for variety | Valkanova, 80.lv |
| Sébastien Lagarde's rain study | wetness and puddles by water held, dried in order | Lagarde |

### What the masters teach, one lesson each

| Who | Known for | The lesson for us |
| --- | --- | --- |
| Morten Olsen (Insomniac, then IO Interactive) | the Ultimate Trim; Hitman's material library | a fixed layout lets surfaces swap without touching UVs; base materials keep many hands consistent |
| Morten Mikkelsen (Unity) | hex-tiling | continuous surfaces need a sampler that never repeats; normal maps gain most |
| Inigo Quilez | texture repetition | per-tile offsets hide tiling where seams are hidden; a smooth index costs two fetches |
| Sébastien Lagarde | wet surfaces | wetness is an order of events, set by how much water a place holds |
| Anastasia Opara (Pounce Light) | Tiny Glade's walls | a smooth field per vertex, a ragged edge in the shader |
| Jasmin Patry (Sucker Punch) | Ghost of Tsushima's light | a physical base with artists' controls on top; grading in lookup tables |
| Jane Ng (Campo Santo) | Firewatch's world | detail rationed to what matters; atmosphere over accuracy |
| Gregorios Kythreotis (Shedworks) | Sable | fog first; fade, never pop |
| Yannick Gombart (Arkane) | Dishonored 2's materials | medium-scale detail; dirt uneven, with calm places |
| Fanny Vergne (Blizzard) | World of Warcraft's environments | neutral values in the texture; light carries the mood |
| Tsvetelina Valkanova (Ubisoft) | Valhalla's materials | four layers of detail; a constant texel ratio across a near and far blend |
| Jonathan Benainous | Assassin's Creed Odyssey and The Last of Us Part I materials | one vertex channel per layer: cracks, moss, wet |
| Joost van Dongen (Ronimo) | interior mapping | a room behind every window for a few instructions |
| Eric Paquette, Pierre Poulin, George Drettakis | paint cracking and peeling | cracks where stress beats strength; peels where adhesion is lost |
| Michael Toksvig (NVIDIA) | mipmapping normal maps | detail too small to see becomes roughness |

## 2. The painterly read at scale

**Firewatch.** Campo Santo's art came from Olly Moss's key art: flat shapes, strong silhouettes, colour in distinct depth layers, a colour script tied to the story, fog for distance; the sky often fills half the screen (Jane Ng, GDC 2015, thumbsticks, secondary). Narratively important objects got more texture detail than the rest, which taught players what mattered (same). The sky was a shader built on colour and tone rather than Rayleigh and Mie, because artists could not steer the physical terms, and Olly Moss painted reference skies live while the programmer watched to find which controls it needed (Campo Santo blog). The same programmer built "a directional stylistic fog system" and shaders for "painterly distant mountains" (Campo Santo blog, 5 September 2014). Jane Ng hand-modelled 23 trees and sized things by feel, not measurement (80.lv). Lesson: detail is rationed to meaning; distance is a painted shader of its own.

**Sable.** Flat shading gave Shedworks few depth cues, so they layered lighting, fog and lines; distant fog was "really, really key" for readability, and lines fade with distance, because without fading, distant objects popped in (Gregorios Kythreotis, GDC 2022, Game Developer). Content sits in islands with calm between (same).

**Dishonored 2.** Arkane's materials were painted by hand to remove photo noise: a tool generated a base, which artists painted over with shared brushes for one look. Too much fine detail would wash out the style, so they worked at medium scale. Dirt and wear went on unevenly, noisy in some places and calm in others (Gombart, 80.lv). Sébastien Mitton's mantra: "Art is not graphics" (Journal du Geek, secondary).

**World of Warcraft.** Hand-painted textures paint how light meets a surface, but Vergne keeps values neutral and leaves mood to lighting and ambience, since extreme values crunch or blow out detail (80.lv). That is SEASON's lesson from the other side: paint the material, not the light.

**Disco Elysium.** The backgrounds are painted from renders of a fixed camera, with height, normal and shadow maps for each painted frame so real-time characters and objects sit in them; everything that moves or can be picked up is real-time (ZA/UM developer blog via GameBanshee, MCV; secondary). A free camera rules this out for us. What transfers is the bake: a painter's decisions written into a texture once, then lit.

**Arcane.** Fortiche painted textures on 3D surfaces (Mari was "essential") and leaned on matte paintings for environments (Fortiche, FMX 2025 summary, secondary). Hand-painting at that level across a town is out of reach (`docs/research/reality-check.md`); the lesson is the brush's scale, kept constant in the world.

**Ghost of Tsushima.** Sucker Punch called it "stylized realism". The base is physical: light, atmosphere, and haze from 10 cm to 100 km, with local tonemapping. On top sit artists' controls: white balance set by picking the colour white should become, global adjustments, and grading in 32-cubed lookup tables the art director preferred (Jasmin Patry, SIGGRAPH 2021). The fields of grass are millions of procedural blades (Wohllaib, GDC 2021 abstract), but their read is wind and colour at the scale of the field.

**Level of detail as art.** Robin Mendoza's essay treats an LOD system as an "artistic codec" (Game Developer, 2023). Skyward Sword and Love use an impressionistic distance filter. Shadow of the Colossus moves from soft billboard to simple mesh to full geometry "like dispersing a veil". A uniform fidelity everywhere makes a flat image.

**What they share.** The read lives in value and air; detail is medium-scale and rationed; textures carry material, light carries mood; things fade in and never pop; distance is drawn as its own style. All five are already rules in `docs/visual-direction.md`. What is new is how to keep them when a surface carries history at every distance (section 3).

## 3. How history survives distance

### What a pixel covers

At 1440p with the street stop's 38-degree vertical lens, a pixel spans about 0.46 mm for every metre of distance, more at a grazing angle:

| Distance | A pixel covers | What reads | Our tier |
| --- | --- | --- | --- |
| 1 m (at its foot) | 0.5 mm | grain, crusts, sand, a lamina's step | near |
| 5 m | 2.3 mm | crusts as shapes, chamfers, cracks | near |
| 10 m (street stop) | 4.6 mm | a few painted marks a piece, joints, the hollow | near, painted |
| 20 m | 9 mm | value plates, board laps, courses | street |
| 80 m | 3.7 cm | a flight as banded values, a house's coats as colour | city |
| 400 m | 18 cm | masses in air | far |

`OS_Near` in `Detail.hlsl` already uses this: near detail is full at a footprint of 1.2 mm and gone by 4 mm, about 2.5 m and 9 m away. Our slate grain at 0.5 mm a texel matches the eye at a metre. Typical published targets are about 5 pixels a centimetre for third-person games and 10 for first-person (Maxon documentation; practitioners). Ours is twice first-person: right for steps under the feet, too much for walls and roofs.

### Four rules from the studies

1. **The same data at every tier.** Unreal's HLOD merges a cluster's meshes into one proxy and bakes their materials into one, with a gutter of padding between UV islands so colours do not bleed in the mips, and can carry vertex colours into the proxy (Epic documentation). The history must be baked from the same fields as the near tier's, never re-derived.
2. **Each mark resolves to its mean, not to nothing.** Toksvig's method reads how much a mip-filtered normal has shortened and widens the specular lobe by it, so ridged or rough detail that falls under a pixel becomes roughness instead of sparkle or vanishing (NVIDIA, 2004). Our growth layer does this for lichen ("seen as its mean, as a lens would average it"); the grain's relief and the polish should do it too, or a polished, ridged step will change value when its relief fades.
3. **But mean alone is grey mush.** A painter simplifies into a few shapes. Our history budget (`docs/living-fabric.md`) says each view tells a measured number of histories, marks from one cause drawn as one shape. At the street stop, a history field should be drawn as two or three soft value plates (the walking line, the quiet end, the damp foot), its edges painted, before it is averaged at the city tier. Anisotropic Kuwahara filtering flattens an image into painted regions along its feature directions while keeping shape boundaries, in real time on the GPU (Kyprianidis, Kang and Döllner, 2009); run offline on a city-tier bake, it could turn baked history into painted plates at no runtime cost (untested).
4. **Fade, never pop.** Sable's lines fade by distance; Shadow of the Colossus dissolves its veil. Every tier switch should cross-fade (URP's LOD cross-fade dithers) and the switch distance should be where the two tiers match in value, measured.

### Where history lives so it survives

Per-vertex history survives only as long as its vertices do. Decimate a mesh and the fields blur, shift or break. Attribute-aware simplifiers help: meshoptimizer weights attributes in the error (texture coordinates at about 10 to 100), preserves attribute seams by default and lets vertices be locked or prioritised (MIT; README). Unity 6.2's own Mesh LOD generator does not say how it treats UVs, and its troubleshooting page shows texture faults at lower levels (Unity documentation). The safer answer is the one HLOD uses: history in a texture with a parameterisation every tier shares, so the mesh can change freely.

## 4. Our stack against all this

### What we do right, and keep

- **Masks from facts and geometry.** No surface is hand-painted for its history; the water layer, wear, growth and repairs come from causes. This is where Cyberpunk and Naughty Dog spend artist time, and where we spend none.
- **Pigment-only, painted grain at our scale**, read in each piece's own plane at its own offset and turn (`blender/parts/stone/slate/paint.py`). It matches Quilez's per-tile technique, Vergne's neutral values and SEASON's lesson.
- **`OS_Near`: true up close, painted from afar,** one shader for every distance. It is the industry's distance blend done by pixel footprint rather than by tier.
- **Water by gravity,** with each material's water profile; growth as rosettes from points in their years; repairs as their own materials with dates. These are the layers Naughty Dog and Lagarde built as separate features, unified.
- **One shade function** and no shadow tint in any material.
- **Generated parts with real chamfers,** so no trim bevels in normal maps and no bevel seams.

### What the census says about stone

We ran the gully generator headless and counted triangles by face kind (`blender/generators/stone.py`, `lay()`):

| Flight | Vertices | Triangles | Split faces | Tops | Rounded edges | Joint soil | Pointing and dabs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 (29 steps) | 51,250 | 97,985 | 51,700 (53%) | 26,058 (27%) | 15,840 (16%) | 3,248 | 1,139 |
| 1 | 135,629 | 263,297 | 149,074 (57%) | 67,752 (26%) | 39,368 (15%) | 3,226 | 3,877 |

The split faces are not millimetre texture. Each plate stands in or out by 1.2 to 2.2 cm in flat facets between kinks, with a facet ring every 5 cm down a tall band (`slab.py`), because flatter faces read as planks or soap in review. At the street stop a pixel is about 5 mm, so the plates read there, and they earn their geometry. Every vertex is jittered, though: a limited dissolve in Blender at 5 degrees removed not one triangle. So the only way to fewer triangles is to accept a small error.

We measured that error. Blender's Decimate (collapse), run headless on flight 0, deterministic over two runs:

| Kept | Triangles | Median error | 95th percentile | 99th percentile |
| --- | --- | --- | --- | --- |
| all | 97,985 | 0 | 0 | 0 |
| 60% | 58,791 | 0.07 mm | 0.76 mm | 1.3 mm |
| 45% | 44,092 | 0.26 mm | 1.4 mm | 2.2 mm |
| 35% | 34,294 | 0.44 mm | 2.0 mm | 3.0 mm |
| 25% | 24,495 | 0.71 mm | 2.8 mm | 4.3 mm |

(Error is each original vertex's distance to the decimated surface; the largest, about 13 mm, sits at a few chips.) At 10 m a pixel is 4.6 mm, so a third of the triangles is invisible from the street stop, and a quarter is invisible from 20 m. Within a few metres, at eye level, the full part stays.

Three things stop us using this today.

- **History rides on the vertices.** Polish, lichen years, moss and water held sit in UV4 and UV5, the water layer and face kind in UV2, the sky and ground bake in UV3. Decimation blurs and shifts them; a coarser grid coarsens them. The tops' 8 cm grid is there for history as much as for the hollow.
- **Six UV channels on 135,000 vertices.** Position, normal and six two-float UV sets come to roughly 80 bytes a vertex: about 4 MB for flight 0 and 11 MB for flight 1, before any tiers.
- **The budget.** The foundations give a stone piece up to 600 triangles at the near tier and a flight about 2,000 at the city tier. The measurements say the near budget is about right beyond a few metres, once the mesh is free to change.

### What breaks at the houses

The house generator draws boards as real lapped geometry (`building.py`, `_clad`) coloured from a 16-swatch palette texture (`palette.py`). Boards should stay geometry: the laps make the comb of shadow lines in low sun and the silhouette at corners and eaves. But a lapped board is a strip a few triangles long, so per-vertex fields cannot carry a drip under a sill, the line where a coat gave up, or a ghost sign. Tiny Glade's vertex field is a smooth distance to a few windows; ours would have to hold a drip under every sill, along boards that have vertices only at their ends. The coat stack (`docs/building-system.md`, Surfaces) needs centimetre resolution in texture space, and every later material (render, roofing, concrete) needs the same.

### What should change now, before the houses

1. **History moves into history maps.** One small texture (or two) per merged run (a flight, a wall run, a facade, a roof slope), at about 2 cm a texel under the feet and 4 to 8 cm on walls and roofs. The address needs no unwrapping tool: every piece already has metric piece-local UVs (UV0: the top in metres, the faces round and up), so each piece gets a rectangle in its run's atlas and its atlas UV is that rectangle's origin plus its own coordinates. Every tier generated from the same piece writes the same address, so tiers share history by construction. The generator rasterises the fields it already computes into the atlas with numpy, dilates each island by a few texels (Unreal's gutter), and the shader reads one or two extra samples. Identity stays per vertex: face kind, piece seed, wall or board id. The shader keeps thresholding smooth fields with noise for crisp edges, as Tiny Glade does.
2. **Stone's tiers by measured error.** The full part within about 5 m (eye level, scenes); the part decimated to about a third from 5 to 20 m (95 percent within 2 mm); a quarter or less from 20 to 80 m; the merged run beyond. Decimation runs in the generator after the history is written to the map, and the atlas address is recomputed from each piece's own coordinates, so nothing about history depends on which vertices survive. Judged A/B in grey light at the switch distances.
3. **Timber gets an atlas and a coat stack** (below), so the house's walls, trims and doors are drawn by one paint system with the board and trim geometry the generator already makes.
4. **Each material becomes a record** (section 5), so a new material is a day, not a week.

### Where each kind of data lives

| Data | Scale | Home | After |
| --- | --- | --- | --- |
| identity: grain, boards, tiles, tooling | millimetres to centimetres, repeating | painted tiling textures and atlases, sampled per piece at its own offset and turn; one texture array per family | Cyberpunk's templates |
| which piece, which face, which wall or board | per piece | per vertex, constant over the piece | survives decimation; indexes the data |
| shape masks: distance to an edge, sky and ground seen | follows the mesh | per vertex on dense parts (trims, frames); in the history map on broad ones | Substance's curvature and occlusion |
| history fields: polish, lichen years, moss, water held and run, exposure | centimetres to metres, smooth | history maps, 2 to 8 cm a texel | Unreal's HLOD bake |
| town fields: feet, water on the ground, sky, wind and salt | metres | maps over the town (the sky map exists) | The Division's world mask |
| facts per thing: coats, years, care | per thing | a data texture indexed by id | no `MaterialPropertyBlock` under the GPU Resident Drawer |
| discrete facts: a sign, a poster, a rust run | local | mesh decals from an atlas | The Division's separate marks |
| fine marks: crusts, sand, crazing, peel edges | under a millimetre to centimetres, made by rule | the shader, thresholded on the fields and faded by `OS_Near` | Tiny Glade's field and noise |
| weather now | the whole town | shader globals read with the water field | Lagarde's order of drying |

### Worked through: the gully's history map

Flight 0's faces cover 150 square metres, the hidden beds included (measured from the generator). The beds need no history, so the atlas holds about 100 square metres: at 2 cm a texel, about 250,000 texels, which packs into 1024 by 512. Two maps carry what UV1 to UV5 carry today:

| Map | R | G | B | A |
| --- | --- | --- | --- | --- |
| history | polish | lichen years / 200 | moss | water held |
| place | the water layer (lands, runs, drips) | sky seen | ground seen | years bare / 200 |

Uncompressed, the two maps take 4 MB, about what the flight's vertex data takes now; compressed (BC7, one byte a texel each), about 1 MB with mips. Decimated to a third, the mesh has 18,221 vertices (measured), and with three UV sets (grain, atlas address, face kind and seed) it takes well under 1 MB. The flight goes from about 4 MB to under 2 MB, and the street and city tiers read the same maps at their mips for nothing.

The generator already computes each field per vertex. Writing them into the atlas is a numpy loop over triangles in atlas space with barycentric fill, then a dilation of four texels round each piece's rectangle so mips do not bleed (Unreal's HLOD gutter). The shader's change is small: `hist` and `water` come from two texture samples at the atlas UV instead of from UV4 and UV5, and every rule after that stays as it is.

The risk is the edge. A field stored at 2 cm and drawn bilinear has soft edges, where today's 8 cm vertex grid has softer ones; the crisp edges come, as now, from noise thresholded against the field (`OS_LichenAt`, `OS_Streak`). So nothing should look softer; the A/B in grey light at eye level is the check.

### The recommended way to build each material family

| Family | Geometry | Texture | Per vertex | History map and fields | Procedural in shader | Decals |
| --- | --- | --- | --- | --- | --- | --- |
| Stone, laid (steps, setts, kerbs, walls) | the full part (plates, chamfers, nosing, hollow) within about 5 m; decimated by measured error beyond | painted grain at 0.5 mm for walked stone, 1 mm for walls; relief in alpha | face kind, piece seed | polish, lichen years, moss, water held, water run, sky and ground bake | crusts, sand, crazing, streaks, edges of every field | cement dabs as parts near; in the map from the street tier |
| Timber cladding | every board and lap, corner boards, butt joints | board atlas at 1 mm: strips by profile (plain lap, beaded, double-rabbet), grain, knots, nail lines | wall id, board id and seed | exposure (sun, rain, sky), drips below sills and cornices, splash at the foot, hands by the door | coat survival and peel edge, crazing cells, grain through thin coats | ghost signs, painted lettering, a replaced board's fresh coats |
| Paint (on timber, iron, render) | none of its own | none: colour comes from the coat table | (from its host) | the host's exposure | the coat stack | signs, posters |
| Trims, windows, doors | profiles with real chamfers | trim atlas at 1 mm, shared with boards | edge distance (dense meshes), trim id | as the wall | edge wear from edge distance and hands | numbers, plates |
| Glass | panes, bars, putty | glass wave normals by era; interior atlas | pane id and seed | care field for grime | interior mapping, reflection distortion, grime from corners | stickers, notices |
| Roofing (tile, slate, Eternit, felt, tin) | courses as strips; the wavy eave and verge; corrugations | tile or slate face at 2 mm | course and tile index from UV | water (run down the courses, lingering at overlaps), sky (north slopes) | odd and replaced tiles by index, lichen and moss | felt patches, tin patches |
| Render and brick | wall planes, openings, cornices | render and brick at 1 mm, hex-tiled | wall id | as timber | patching, spalls, salt bloom, soot | patches in the era's mix |
| Concrete and asphalt | casts with arrises, formwork lines; asphalt edges | 1 mm, hex-tiled | cast id | water, wear | aggregate showing with wear, cracks along the field | trench strips, patches |
| Metal (rails, covers, lamps) | the parts | small atlases | part id | water from above | rust from fixings, paint coats | rust runs below fixings |

Notes on the four house families, the bulk of the town:

**Timber and paint.** Each wall carries its coat table, read from a town-wide data texture indexed by the wall id on its vertices: up to eight coats, each a colour, a year, and a paint kind (linseed oil, alkyd, acrylic, limewash, tar) with its primer (ochre-primed or not). The GPU Resident Drawer refuses objects that use `MaterialPropertyBlock` (Unity documentation), so per-thing facts must come this way. Each coat's survival at a point is a height blend: its adhesion plus a peel pattern of its kind, minus the exposure field times the years since it was put on. The visible coat is the topmost that survives; where none does, bare wood greys with its years exposed. The kinds follow `docs/research/house-changes.md`: linseed chalks and thins evenly, so the grain shows through on the sunny side; ochre-primed coats craze in small cells; plastic paint over oil flakes in sheets with sharp edges; limewash powders. Paquette, Poulin and Drettakis model why: cracks open where tensile stress beats the paint's strength, and loss of adhesion decides how a peel curls (Graphics Interface 2002); we draw their result as rules, not their simulation. At the near tier a peel's lip lifts in the normal and holds a line of dirt; at the street stop the coats read as patches of colour; at the city tier the wall is the area-weighted mix. A replaced board starts its own coat list in its year, so it reads fresher than its neighbours (`docs/upkeep.md`).

**Glass.** Glass is a fact by era: older panes wavy, later sheet and float glass flat (dates for this coast unverified), each pane's wave seeded, so one flat pane among wavy ones tells of a broken pane replaced. Behind it, interior mapping (Joost van Dongen, Game Developer). Per pixel, a ray from the eye is followed into the building, and the room it enters is found from the regular spacing of floors and walls. Only the ceiling or floor and two walls are intersected, a few steps each. Rooms are picked from an atlas; furniture needs extra flat layers at extra cost. SimCity (2013) used it, according to one of its programmers, and Unreal ships it as a node (same). Our atlas is by era and household, and lit or dark from who is home at the hour.

**Roofing.** The city camera sees roofs more than anything. Courses are geometry: they make the comb of lines in low sun and the wavy eave of curved tile against the sky. A tile's outline within a course lives in its texture, except at the eave, verge and ridge, where it is the silhouette. A tile's index comes from its course and its position along it, so an odd or replaced tile (from the roof's upkeep, with its year) takes another tone and starts its own lichen. Water runs down the courses and lingers at the overlaps; north slopes take moss, south slopes lichen.

**Render, concrete and asphalt** are continuous fields with no joints to hide seams: they get hex-tiling (Mikkelsen) on their painted textures.

### Worked through: a wall's coats

The board atlas is painted in numpy like the slate's grain: about 4 m by 1 m at 1 mm a texel (4096 by 1024). It holds strips by profile (the plain lapped board, the beaded board of the chalet years, the 1970s vertical board), each tiling along its length without a seam. R holds the wood's lightness (grain, knots), G its relief, B the knots (resin bleeds through paint over the years), A the end grain at butt joints. Each board samples a seeded strip at a seeded offset, as each slab samples the grain. Nail rows follow the studs at about 60 cm, drawn by rule from the board's id, and rust through old coats.

A wall's coat table, read by wall id, lists its coats oldest first. The shader works down from the top:

```
exposure = facade map at this point        // sun and rain facing, drips under sills, splash, hands
for each coat i from the top down:
    worn_i  = exposure * (now - year_i) / life(kind_i)
    holds_i = adhesion(kind_i, primer_i) + peel(kind_i, q, seed) - worn_i
    if holds_i > 0: show coat i, chalked and faded by its own age; stop
    if the interface under coat i is weak (plastic over oil, anything over ochre primer):
        the coats above it went together as a flake; skip to the coat below the interface
nothing holds: bare wood, silvered by its years bare
```

`peel` is the paint kind's own pattern: a soft, even thinning for linseed; small polygonal cells for crazing; large sheets with sharp edges for plastic over oil; a powdery fringe for limewash. Near the camera, a coat's edge lifts in the normal and holds a thin line of dirt; from the street stop, coats read as patches of colour; at the city tier, as their area-weighted mix. A sign painted on a wall is a decal with its own coat table, so it shows through where the coats over it wear, which is a ghost sign by rule.

### Decals: where a fact gets its own mark

A field gets a layer; a fact with a place gets a mark; texture claims nothing. Ghost signs, painted lettering, posters (records, which may be wrong), rust runs below a fixing, a felt patch, the outline left by a removed shopfront: each is a mesh decal placed by the generator from the diary, from one atlas per family, dated. A decal is drawn by the same surface stack as its host, so it gets wet, grows lichen and fades by the same rules; for the street and city tiers it is baked into the run's history map. URP's Decal Projector is kept for scene state that comes and goes (a spill, chalk, wet footprints), few and near, because its DBuffer mode costs a depth-normal prepass.

### Distance, per tier

| Tier | Geometry | History | Material |
| --- | --- | --- | --- |
| Near, within about 5 m | the generator's full part | history map at full resolution; marks true up close (`OS_Near`) | grain at full resolution |
| Near, 5 to 20 m | the part decimated to about a third (for the gully, 95 percent within 2 mm) | the same map; marks painted | grain mips |
| Street | decimated to a quarter or less (95 percent within 2.8 mm at a quarter) | the same map; fields drawn as two or three painted plates; roughness takes the faded relief (Toksvig) | grain mips |
| City | a run or a house merged, about 2,000 a flight and 1,500 a house | the map's mips, or the albedo with history baked in (no light) | the bake |
| Far | impostors or the terrain's colour | from the same bake | the bake |

Each switch is checked by rendering both tiers at the switch distance and comparing them at one-eighth size in greyscale.

## 5. Materials as data

A material is a record in the setting pack, read by the Python generators and by a Unity editor step that writes the material asset (a saved material keeps its values; a shader default never reaches it). The record holds:

- its identity: family, name, the era range it is sold in;
- pigment: fresh and weathered colours and the years to weather between them, checked for value against its neighbours;
- grain: the painter script and seed that make its atlas, the texel density, its relief depth;
- tooling: how it was worked (split, sawn, dressed, cast, planed);
- water profile: the four numbers `Water.hlsl` reads, and rain exposure;
- wear: hardness and polish (the `STONES` dict's numbers move here), crack rate;
- growth affinity: how readily lichen and moss take it (Eternit and lime high, fresh cement low);
- for paints: life by exposure and failure mode (chalk, craze, flake, powder);
- tiers: what its city-tier bake keeps.

Painted textures of a family go into one texture array, so every timber surface in the town shares one shader and one material, indexed per vertex. The equivalents elsewhere are Cyberpunk's `.mltemplate` library and Unreal's layer assets. Ours differs in where the masks come from.

## What we should do

Ranked. Days are working days for Claude at the current pace, before review.

| # | Change | Cost | Quality it buys | Speed it buys |
| --- | --- | --- | --- | --- |
| 1 | **History maps** for every run: piece rectangles in an atlas from piece-local UVs; numpy rasterising and dilation; shader reads the map; identity stays per vertex. Stone first, as the proof | 3 days | history at 2 cm independent of the mesh; tiers share it; the houses become possible | meshes can be simplified and tiered freely; vertex data roughly halves |
| 2 | **Stone's tiers by measured error:** Blender's Decimate in the generator after history is written; atlas address recomputed from each piece; the full part within about 5 m, a third to 20 m, a quarter beyond; judged A/B at the switch distances | 1 to 2 days | the plates and hollows kept where they read; less aliasing at the street stop | flight 0 from 98,000 to 34,000 triangles past 5 m, 24,000 past 20 m |
| 3 | **Timber atlas and the coat stack:** a board and trim atlas painted in numpy; the coat table in a data texture; survival as a height blend by paint kind; facade exposure maps from the water and sky fields | 5 to 6 days | the town's dominant surface carries its decades; ghost coats and replaced boards for free | one system draws every wall, trim and door of every era |
| 4 | **Material records** in the pack, written to Unity materials and texture arrays by an editor step; `STONES` and the water profiles move in | 2 days | one source of truth; the foreign-pack check becomes a new record | a new material in about a day |
| 5 | **Mesh decals from facts:** an atlas per family; the generator places them from the diary; drawn by the surface stack; baked for far tiers | 3 days | ghost signs, posters, rust runs, patches as facts | each new mark is an atlas cell and a rule |
| 6 | **Glass:** era glass with seeded waves; interior mapping with an era atlas; lit from facts; grime from care | 4 days | blue hour's lit windows read as rooms | windows by era are data |
| 7 | **Roofing:** courses as geometry, tiles in texture, odd tiles by index from upkeep, growth from the roof's water and sky | 3 days a roof family | roofs hold from the city camera, the main view | roof families share one shader |
| 8 | **Distance rules:** Toksvig on the grain's relief; history fields as two or three plates at the street stop; the tier-flip check in the frames | 2 days | no value pop between tiers; painted plates instead of mush | tiers can be judged by a number |
| 9 | **Hex-tiling** for render, concrete, asphalt and ground | 1 day | no visible tiling on continuous surfaces | none |
| 10 | **The city-tier bake with anisotropic Kuwahara,** as an experiment on the gully at 80 m | 2 days | possibly a painted read at distance for free | if it works, every run's far tier is a bake |

Items 1 to 4 come before plan step 2's first house part.

## Gaps

- Primary sources that would not open: the Uncharted 4 technical art slides (13 MB, too large), the GDC Vault talks on Uncharted 4's Substance pipeline, Ghost of Tsushima's landscapes, Assassin's Creed Odyssey's texturing, Hitman's material library and Sunset Overdrive's trim (abstracts only), and Benainous's portfolio (blocked). Naughty Dog's exact blend shader is known only from portfolios and forums.
- No official word on the material pipelines of Red Dead Redemption 2 or Kingdom Come: Deliverance 2, on Tiny Glade's beyond one sentence, on Townscaper's materials, or on Insomniac's interiors (van Dongen suspects interior mapping; Insomniac has not said).
- Cyberpunk's multilayer is documented by modders, not CD Projekt Red; its microblend is undocumented.
- Not yet measured on our side: the per-pixel cost of `Growth.hlsl` and `OS_Noise` at 1440p, for the performance study to time. History-map memory at town scale. Whether BC7 compression shows blocks in a smooth field (if it does, the maps stay uncompressed). Whether decimation's few large errors (about 13 mm, at chips) show at the switch distance. Whether a Kuwahara bake reads as painted or muddy. Our estimate for a house: walls and roof of about 430 square metres take about 70,000 texels at 8 cm, so 70 to 140 KB compressed for one or two maps before mips, and mip streaming is needed beyond a few thousand houses.
- Dates for glass by era on this coast (cylinder, drawn sheet, float) are unverified.
- Unity's Mesh LOD does not document how it treats UVs and extra channels; history maps sidestep it.

## For Øystein to decide

1. History moves from vertices into history maps before the houses (recommended; it changes how the gully is built, not how it looks).
2. Stone's switch distances by measured error (the full part within about 5 m, a third to 20 m), each switch judged A/B in grey light and kept only if he cannot tell the two apart.
3. Texel targets: 0.5 mm for stone under the feet, 1 mm for walls, trims and paint, 2 mm for roofs.

## Sources

Studios and engines: [Cyberpunk multilayered (redmodding wiki)](https://wiki.redmodding.org/cyberpunk-2077-modding/for-mod-creators-theory/materials/multilayered) · [Cyberpunk modding docs](https://github.com/CDPR-Modding-Documentation/Cyberpunk-Modding-Docs/blob/main/for-mod-creators-theory/materials/multilayered/README.md) · [CDPR texturing pipeline (80.lv)](https://80.lv/articles/the-texturing-pipeline-in-substance-tools-for-cyberpunk-2077) · [Unreal material layers](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-material-layers-in-unreal-engine) · [Unreal HLOD](https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition---hierarchical-level-of-detail-in-unreal-engine) · [Fallout 4 material swap](https://falloutck.uesp.net/wiki/Material_Swap) · [AC Valhalla materials (80.lv)](https://80.lv/articles/a-look-at-the-material-workflow-in-assassin-s-creed-valhalla) · [AC Odyssey texturing (GDC)](https://www.gdcvault.com/play/1026145/Texturing-the-World-of-Assassin) · [Dérozier](https://vincentderozier.artstation.com/projects/9vk0L) · [Hitman material library (GDC)](https://gdcvault.com/play/1027518/Hitman-Building-a-Material-Library) · [Uncharted 4 materials (GamesBeat)](https://gamesbeat.com/how-uncharted-4s-artists-created-their-amazing-landscapes/) · [Technical Art of Uncharted 4](https://advances.realtimerendering.com/other/2016/naughty_dog/index.html) · [Uncharted 3 blending (Polycount)](https://polycount.com/discussion/comment/1573696) · [Benainous, TLOU Part I](https://jonathan_benainous.artstation.com/projects/g8do3x) · [The Division optimisation (80.lv)](https://80.lv/articles/optimisation-of-content-and-levels-in-the-division) · [Samurai Landscapes (GDC)](https://gdcvault.com/play/1027352/Samurai-Landscapes-Building-and-Rendering) · [Procedural grass in Ghost of Tsushima (GDC)](https://gdcvault.com/play/1027214/Advanced-Graphics-Summit-Procedural-Grass) · [Patry, Real-time samurai cinema](https://www.advances.realtimerendering.com/s2021/jpatry_advances2021/index.html) · [Tiny Glade windows (80.lv)](https://80.lv/articles/procedural-windows-in-pounce-light-s-tiny-glade-get-an-upgrade) · [Dishonored 2 materials (80.lv)](https://80.lv/articles/asset-material-production-in-dishonored-2/) · [Mitton (Journal du Geek)](https://www.journaldugeek.com/dossier/dossier-dishonored-2-direction-artistique/) · [Ultimate Trim (GDC)](https://gdcvault.com/play/1022323/The-Ultimate-Trim-Texturing-Techniques) · [Trim sheet notes](https://3dreference.notion.site/Trim-Sheets-e6e86d4155f845e3bb3ed6b04b0c6cab) · [Vergne (80.lv)](https://80.lv/articles/the-strings-of-environment-design/) · [DOOM 2016 graphics study](https://www.adriancourreges.com/blog/2016/09/09/doom-2016-graphics-study/) · [Sea of Thieves notes (Habrador)](https://blog.habrador.com/2018/08/stylized-graphics-fortnite-sea-of-thieves.html) · [Sea of Thieves talk (Game Developer)](https://gamedeveloper.com/art/video-how-rare-crafted-the-look-and-feel-of-i-sea-of-thieves-i-)

Painterly: [Firewatch sky (Campo Santo)](https://blog.camposanto.com/post/112703721804/this-blog-post-is-an-in-detail-explanation-of-part) · [Campo Santo on fog and distant mountains](https://blog.camposanto.com/tagged/unity) · [Art of Firewatch (thumbsticks)](https://www.thumbsticks.com/gdc-2015-the-art-of-firewatch) · [Making the world of Firewatch (80.lv)](https://80.lv/articles/creating-the-world-of-firewatch) · [Sable readability (Game Developer)](https://www.gamedeveloper.com/marketing/how-shedworks-refined-the-art-of-sable-in-pursuit-of-readability) · [Disco Elysium render to paintover](https://www.gamebanshee.com/k4fuh) · [Disco Elysium (MCV)](https://www.mcvuk.com/business-news/we-knew-immediately-that-we-needed-to-make-a-game-with-a-striking-and-unique-look-to-accompany-the-writing-a-look-that-would-balance-the-mundane-with-the-unfamiliar-and-strange-the-art) · [Fortiche at FMX](https://forticheprod.com/?p=10690) · [Level of detail as artistic codec](https://www.gamedeveloper.com/art/level-of-detail-as-artistic-codec)

Techniques and papers: [Substance metal edge wear](https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/effects/generators/metal-edge-wear) · [Layering in Substance Designer (The Rookies)](https://discover.therookies.co/2021/04/18/layering-details-in-substance-designer-to-achieve-realistic-3d-props-and-environments/) · [Mishkinis, terrain splatting](https://www.gamedev.net/articles/programming/graphics/advanced-terrain-texture-splatting-r3287) · [Lagarde, Water drop 2b](https://seblagarde.wordpress.com/2013/01/03/water-drop-2b-dynamic-rain-and-its-effects/) · [Quilez, texture repetition](https://iquilezles.org/articles/texturerepetition/) · [Mikkelsen, hex-tiling (JCGT 2022)](https://jcgt.org/published/0011/03/05/paper.pdf) · [Unity stochastic texturing](https://unity.com/blog/engine-platform/procedural-stochastic-texturing-in-unity) · [van Dongen, interior mapping](https://gamedeveloper.com/programming/interior-mapping-rendering-real-rooms-without-geometry) · [Paquette, Poulin, Drettakis 2002](https://graphicsinterface.org/wp-content/uploads/gi2002-8.pdf) · [Toksvig, mipmapping normal maps](https://developer.download.nvidia.cn/whitepapers/2006/Mipmapping_Normal_Maps.pdf) · [Kyprianidis et al., anisotropic Kuwahara](https://diglib.eg.org/handle/10.2312/CGF.v28i7pp1955-1963) · [meshoptimizer](https://github.com/zeux/meshoptimizer) · [Maxon, texel density](https://help.maxon.net/c4d/en-us/Content/html/Texel_Density.html) · [Modo planar decals](https://learn.foundry.com/modo/Content/help/pages/decals/planar_decals.html) · [Star Citizen decals (Polycount)](https://polycount.com/discussion/comment/2576073)

Unity: [URP decal renderer feature](https://docs.unity3d.com/Manual/urp/renderer-feature-decal-reference.html) · [GPU Resident Drawer](https://docs.unity3d.com/6000.3/Documentation/Manual/urp/gpu-resident-drawer.html) · [Making objects compatible](https://docs.unity3d.com/Manual/urp/make-object-compatible-gpu-rendering.html) · [Mesh LOD troubleshooting](https://docs.unity3d.com/Manual/lod/mesh-lod-troubleshooting.html) · [Streaming virtual texturing requirements](https://docs.unity3d.com/Manual/svt-requirements-compatibility.html)
