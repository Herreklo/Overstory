# The corner's growth: how it is built

What the page asks (`reviews/lt1/art-direction/README.md`, The growth): lichen as flat crusts that follow the rock, within 5 L* of it at blue hour, a broken edge, never mounds; heather and grass only where the record puts soil, spiky, never round blobs; moss by wetness, aspect and upkeep; detail gone past 12 m.

## How good studios build it, and what we took

- **Ghost of Tsushima** (Wohllaib and Sobota, GDC 2021): blades placed in Voronoi clumps that share a lean and a hue, each blade a Bézier ribbon (about 13 tris near, 5 far), dark at the root, light at the tip, normals bent toward the clump so it lights as one mass, outline "breakers" kept at a distance. Taken: the clump (a tuft is a fan of blades leaning out from its middle, its normals a dome over it), root to tip, per-clump hue. Not taken: wind, the density per tile (a corner needs hundreds, not millions).
- **Horizon Zero Dawn** (Guerrilla, GDC 2017 and Siggraph 2018): geometry over alpha cards, because alpha testing is what costs and what puffs a far crown out; build the lowest level first and keep its outline. Taken: no cards at all; the far levels are the near tuft's tallest blades, widened, so the spikes hold at every distance.
- **Bad North** (Plausible Concept): border over texture: a shape reads by its edge, not its fill. Taken: the crusts are big shapes with one lobed edge; the tufts' silhouettes carry the growth, their fill is two values.
- **Firewatch** (Campo Santo): far foliage as merged painted masses. Taken: past the focus the per-blade hue fades and the far tufts thin by rank while the kept ones widen, so a far patch is one value, not speckle.
- **Uncharted 4** (Naughty Dog): moss tips lighter than its body; moss a pigment, never a mound. Taken in the painted layer: moss darkens and greens the stone, no height.
- **Connell's lesson** (our own painters): noise is flagged and simplified. Taken: crusts are colonies, never a noise field (a swirl of noise read as camouflage in the first still): seeded discs per cell that merge into scalloped patches as the share rises (reference 15), in two sizes. The big ones are the shapes and hold past the focus; the small ones and the lobed edges are marks, gone past 12 m; under a few pixels a colony becomes its mean.

## How ours is built

- Lichen and moss are drawn in the surface that carries them (`CornerGrowth.hlsl` calls `Shaders/GrowthPaint.hlsl`), from the facts each generator bakes (UV4.y lichen years, UV5.x moss: `growth.on_rock`, the stones' own bake). A share follows the years, the field only says where.
- A tuft is a fixed part per species and variant (`blender/parts/growth/tufts.py`, from the pack), three levels within 72 / 24 / 8 tris. Where it stands is the generator's (`growth.place_tufts`): a seeded jittered grid kept in patches, willowherb in stands along the yard's walls and lip, the path's walked middle bare, the heath only above `heath_above`.
- They draw through our own BatchRendererGroup, culled to the view, crossfaded between levels, no shadows cast, lit by the page's light (`Shaders/GrowthTuft.shader`).
- Budgets are a script (`blender/parts/growth/corner.py` prints them and fails over).
