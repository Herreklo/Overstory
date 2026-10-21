# Ground cover and plants

How the best studios build grass, ground cover and the plants of a town at quality and at a sane cost, and what that means for Overstory. It covers grass and lawns, weeds and grass in joints, moss cushions and mats, heath, ferns, bushes and hedges, gardens, climbers on walls, fallen leaves and litter, and the ground's own colour where plants hand over to it. It closes the craft gap for ground cover in `docs/systems.md` and checks the trees' craft (`docs/research/trees.md`, `docs/trees.md`) against the reference machine, because the birches are to be re-fitted after the building blocks. Drafted on Opus; a lead environment and technical artist's bar.

The sibling studies are not repeated here: what grows where and the plants of Stavanger (`docs/research/vegetation.md`, `nature.md`, `park-trees.md`), performance (`performance-at-scale.md`), materials (`materials-at-scale.md`), the land and its fields (`land-rock-and-water.md`), wind (`animation-and-motion.md`) and light (`lighting-and-colour.md`). Claims seen only in a summary are marked (secondary), unconfirmed ones (unverified). Numbers worked out here are marked (ours).

One limit shaped this study. The session's shared web-search budget ran out part way, and three primary decks were too large to open: the Ghost of Tsushima grass talk, Horizon Zero Dawn's placement and vegetation talks, and Uncharted 4's technical art. Their content here comes from abstracts and write-ups, marked as such. The Gaps section lists what is still to read.

## In short

1. **On the M4 the line that decides everything is opaque against alpha-tested.** Apple's GPUs remove hidden surfaces in hardware before shading, and an opaque fragment lets them skip everything behind it. A fragment that can discard (a leaf card, a grass card, a shell) must be shaded before the GPU knows what it hides. So every layer of cards in a crown or a meadow costs a shading pass (Apple, WWDC 2020). Opaque overdraw is close to free. So near ground cover is opaque geometry, never cards or shells, and cards survive only where few of them overlap.
2. **The best grass is grown on the GPU from fields, near the camera only.** Ghost of Tsushima, Frostbite, Outerra and AMD's samples all work the same way. Blades are generated from a seed per cell, with density taken from maps. They thin with distance while the survivors widen, clump by a cell field, take the ground's colour at the root, and hand over to the ground's own colour further off. Our fields (feet, water, sky, soil, care) are exactly the density maps they read.
3. **Painterly games carry ground cover in the ground's colour; blades only add the near detail.** Firewatch used Unity's detail grass over painted terrain and leaned on fog and colour. Breath of the Wild stores a grass colour and height map with each terrain tile (secondary). Tiny Glade rewrote its grass in 2026 so it looks "fluffier in the distance". For us the ground shader is the main drawer of ground cover from the street stop up, and its far colour should be the near tier's own mean, measured, never painted separately.
4. **Our birches are probably the dearest pixels in the corner.** A birch carries up to 4,200 cards about a metre across, turned to the eye, alpha-tested, over a crown of perhaps 80 m². That is of the order of fifty overlapping card layers a pixel (ours, an estimate). The harness should measure it before the birches are re-fitted. Then come four fixes, in order. Cards are cut to the spray's outline, which saves about half the area (Humus's trimming). An opaque core inside each crown mass hides the back half of the crown for free. A cheap depth-only pass lets each leaf pixel be shaded once. Real leaves, as opaque geometry, come only within about 8 m.
5. **Ground cover is five kinds of thing, built five ways.** Films (lichen, algae, thin moss) stay in `Growth.hlsl`. Mats (lawn, moss mats, heath, crowberry) are a surface lying on the ground with a crisp edge. Tufts and strokes (grass, weeds in joints, heather sprigs, flowers) are GPU instances near the camera. Plants (ferns, bushes, hedges, climbers, garden plants) are things with records, built like small trees. Litter (fallen leaves, needles, cigarette ends) is a deposit field the ground shader draws, with instances near. All five read the same fields.
6. **Every plant has a stable rank, and time moves a threshold.** Seasons (SpeedTree's per-leaf threshold), care (mowing, clipping, weeding, sweeping), succession and wear all work as a potential compared against each candidate's seeded rank. The same tuft appears in the same place every replay, and the yard in 1988 contains the yard of 1987.
7. **Restraint is a fact too.** Swept pavements in five north-European towns, with no herbicide, carried about 1.4% weed cover after a year, most along the edge away from the road (Melander et al. 2009). Green joints everywhere is the stage-set look. The quiet edge, the wall's foot and the empty yard carry the green; the walking line carries none.

## Where we stand

Read from the code and docs on 22 October.

| What | State |
| --- | --- |
| Thin growth | `Growth.hlsl`: lichen as rosettes merging over a century, moss as cushions a few centimetres across in albedo and relief, a film past the street stop; `growth.py` bakes lichen years and moss potential per vertex from damp, traffic, years bare and shelter |
| Wear | `wear.py`: the walking line by flight width, footfall to polish and hollows, `busy()` so growth dies under feet (no plot kept half its cover after 200 passes) |
| Trees | two birches built and closed as a look test; up to 4,200 leaf cards a tree (`PARTS["birch"]["max_cards"]`), clusters 0.85 to 1.3 m on a grown tree, crossed, turned to the eye in the shader about their twig's end (`_OS_FACING`); alpha clip at 0.5 with alpha-to-coverage on (`M_Tree_birch_leaves.mat`) and a hashed clip; coverage-preserving mips; queue AlphaTest; `Tree.shader` at target 3.5, no DOTS instancing, no LOD cross-fade |
| Ground cover, bushes, hedges, climbers, litter | none; designed in words (`docs/nature.md`) |
| The land | clay; its fields (soil depth, wetness, wind and salt, feet) designed in `land-rock-and-water.md`, not built |
| Rendering | URP Forward+, MSAA 4×, GPU Resident Drawer and GPU occlusion off; no performance harness yet |

So nothing is in the way: the ground cover can be designed on the fields and the reference machine from the start.

## 1. How games build grass and ground cover

### What the studios do

| Work | How the grass is built | What we take |
| --- | --- | --- |
| **Ghost of Tsushima** (Sucker Punch; Eric Wohllaib, GDC 2021; the slides were too large to open, details from write-ups, secondary) | A compute pass per render tile places blades on a jittered grid, reads the tile's textures for grass type and height, culls by distance, frustum, occlusion, type and height, and writes instance data. Each tile is one instanced draw with no vertex streams: a blade is a cubic Bézier built from its index, 15 vertices near and 7 far; short blades spend the spare vertices on a second blade. Far tiles are twice the size with the same count, so three blades in four go, and the near shape blends to the far one before the switch. Voronoi clumps share height, colour, facing and lean. Normals are tilted out so a flat blade reads round; blades seen edge-on are thickened in view space; specular normals converge on the clump's normal with distance, against glitter in rain. Far off the field becomes a texture on the terrain, and the terrain takes the grass top's colour. Grass casts no real shadow: the terrain is raised to grass height with dithered depth, plus screen-space shadows. Characters write a displacement buffer the compute pass reads. About 83,000 blades on screen in about 2.5 ms (unverified). | The whole shape: fields in, blades out, near only; clumps as a cell field; the hand-over to the ground's colour; no cast shadows. Its density is a PS4's photoreal meadow, more than our painted look needs. |
| **Horizon Zero Dawn** (Guerrilla; van Muijden, GDC 2017; the abstract and summary page read, the slides too large) | Artists write placement as a graph over world data; the GPU builds a dense world round the player at run time. It places sounds, effects and creatures as well as plants. From a search excerpt of the slides: "fully data driven, deterministic and locally stable", 500 or more asset types, over 100,000 objects, about 250 µs of GPU time (unverified). The vegetation talk (Sanders, GDC 2018) adds a global wind force field, fixed shadow levels per cascade and cross-plane billboards at the last levels (secondary, from a video summary). | Placement as rules over fields, deterministic and locally stable: a local change does not reshuffle the neighbours. |
| **Horizon Forbidden West** (McLaren, GDC 2022, page read) | A visibility-buffer pre-pass with shading in compute, aimed at "foliage and alpha tested geometry". | Even a PS5 needed its own pipeline to afford dense alpha-tested foliage. |
| **Frostbite** (Andersson, SIGGRAPH 2007, notes read in full) | Undergrowth up to about 1 m tall, a couple of instances a square metre, over 2 to 4 km. Cells of 16 m from a pool, chosen by distance, not by frustum, so a fast turn does not spike. The terrain's material masks and normal are drawn top-down into small targets per cell; a pass walks a jittered grid, plays "Russian roulette" against the mask, and tilts each instance by the normal. The cell's position, hashed, is the seed, so every player sees the same grass. The grass shader blends its colour with the terrain's grass colour and lights with the terrain's normal "to look the same as the terrain". | Placement as a threshold against a seeded number per candidate; the grass's colour and normal taken from the ground. |
| **Outerra** (2012 blog, read) | Blades of 7 vertices from a "canopy" field of height and colour at about 30 cm; four blades a canopy point near; each level halves the count and doubles the width; over 400,000 blades within 45 m. The same canopy draws the far land as an envelope of low vegetation, so near and far agree and what hides in the grass stays hidden. | One field drives the near blades and the far colour. |
| **AMD GPUOpen** (mesh-shader grass sample, read) | Blades of 8 vertices; a patch of up to 32 blades falling to 2 with distance; the last blade's width scaled by the fraction left, so nothing pops; survivors widened by the ratio, "barely noticeable" in a dense meadow; normals bent a quarter towards up; the root darkened. | The thinning rule, exactly. |
| **Breath of the Wild** (Nintendo; no primary source opened) | Each terrain tile carries a grass layer of height and colour at 64×64, against 256×256 for the ground's height and material (community reverse engineering, secondary); near the player each blade is one triangle with a colour gradient root to tip (an observer's guess, secondary); geometry chosen over cards to limit overdraw on the Wii U and Switch (secondary). | A coarse grass colour map tied to the ground is what lets grass fade into it. |
| **Firewatch** (Ng, GDC 2016 slides, read) | Unity's terrain detail grass, with the advice to settle the detail resolution early because its cost was unclear; terrain shadow casting replaced by cheap proxies; trees whose alpha cutoff falls with distance, so far crowns read "more puffy". The ground's look is painted terrain, rocks, fog layers and colour. | The painterly read comes from colour, fog and silhouette, not from dense grass. |
| **Tiny Glade** (Pounce Light; Steam developer posts, read) | Grass "twice as fast" after the move to Vulkan (2023); runs on an M1 and on macOS from 2026 after "rewriting half of our graphics engine"; in 2026 the grass was rewritten as one system for all plants, "loosely inspired by 'Nanite Foliage'", much more detailed near and "fluffier in the distance"; a separate far layer that could pop through ("astroturf"); ivy that avoids windows; flowers painted into the meadow. | A dense art-directed meadow runs on Apple silicon; the far grass needs its own design. |
| **Book of the Dead** (Unity, 2018, blog read) | Scanned grass with LODs; hundreds of small instances merged into 15 to 20 patches against draw calls; small vegetation stops casting shadows at about 15 m and is culled at about 25 m; translucency from a thickness map. | Shadows and density end early; nobody misses them. |
| **Unity terrain details** (Unity 6 manual, read) | Instanced meshes recommended; up to 1,023 instances a batch; the healthy and dry colour noise is switched off when instanced, so colour must come from the shader; culled at the detail distance, with a warning that it pops. | Not ours: it knows nothing of our fields and has no fade. |
| **Unity Time Ghost** (2024, page read) | Up to 12 million instances of trees and grass scattered in Houdini, as entities; at most about 8.5 million active, under half a million reaching the renderer. | Offline scatter plus run-time culling, on a high-end PC. |
| **Unreal Engine 5** (Nanite docs, read) | Nanite foliage combines instancing, skinned meshes, voxelisation and animation; masked materials are supported; foliage moved by world-position offset "cannot really occlude itself". | The industry's direction is geometry, not cards, for foliage; it needs a renderer we do not have. |
| **Crysis** (GPU Gems 3, ch. 16, read) | Grass alpha-blended and shaded per vertex because of its fill cost. | Fill is the enemy of grass on every GPU. |
| **Death Stranding** (frame study, secondary) | A plant compute pass each frame; plants pushed by force fields held in small 3D textures; a grass vertex of half-float position, a colour and a UV, no normal; trampling of snow and mud through a top-down depth map. | A blade needs little data. |
| **Red Dead Redemption 2** (frame study, secondary) | Feet, hooves and wheels drawn into a 2048² mud map that drives relief on the terrain. | Wear kept in a texture, not in geometry. |
| **Alan Wake 2** (Remedy, read) | Every visible plant skinned on the GPU, about 300,000 bones a frame at Cauldron Lake; mesh shaders and meshlet culling; wind from signed-distance boxes forming one global field. | One wind field for everything, again. |
| **God of War** (Feeley, GDC 2019 abstract) | A spatial 3D wind simulation; ground plants that answer the player; "card cluster LOD and shadow proxies". | Proxies for shadows. |
| **Animal Crossing** (older games; wikis would not open, unverified) | Grass health per tile, worn by each walk, faster when running and in winter; trodden tiles cannot regrow. New Horizons dropped it. | The first game mechanic of a worn path. |

Not found, or not opened: how Genshin Impact, Sable, Planet of Lana, Kingdom Come: Deliverance 2, The Witcher 3 and The Last of Us Part II build their grass, and the Witcher 4 demo's Nanite foliage beyond Epic's one line.

### Blades, cards or shells

There are four ways to draw grass, and our machine ranks them clearly.

| Way | How | On a desktop card | On the M4 | Who |
| --- | --- | --- | --- | --- |
| Blades as opaque geometry | each blade a strip of 3 to 15 vertices, built from its index | today's standard; cost in vertices and thin triangles | opaque, so overdraw is removed before shading; cost in vertices and in the tiler's buffer | Tsushima, Outerra, AMD, BotW (secondary) |
| Cards with alpha test | a quad or a few crossed quads with a painted cut-out | cheap vertices, expensive fill; aliasing | every layer shaded; the hardware's hidden-surface removal cannot skip them | GPU Gems 1, Unity details, most older games |
| Shells | the ground drawn again in 8 to 32 offset layers, each cut by a noise threshold | fine for short fur and moss | the worst case: many full-screen alpha-tested layers | fur, some stylised grass |
| Ground only | the ground's shader carries the colour, value and relief of what grows | cheapest | cheapest | every game past its grass distance; Firewatch's middle ground |

Two things decide it for us. First, the M4's hidden-surface removal (section 6): opaque blades in a dense meadow cost little more than the front layer, while cards and shells cost every layer. Second, our style. A blade 4 mm wide is under a pixel past about 8 m (ours: 0.48 mm a pixel per metre at 1440p and 35 mm). Fine blades alias and shimmer at the street stop unless they are widened. Painted grass is drawn as strokes, each standing for a few blades. So near ground cover should be opaque strokes: tufts of five to twelve blades a centimetre or two wide, shaped as a painter's marks, about 30 to 80 triangles a tuft. They thin and widen with distance as Outerra's and AMD's do, and are gone into the ground's colour by about 20 to 40 m, depending on the view. Shells are ruled out on this machine.

### Clumping and direction

Every good field in the sources is clumped. Tsushima's Voronoi cells set height, colour, facing and lean towards the clump's centre (secondary); Frostbite's material masks give patches with edges; Broken Roads simulates root density so plants form clumps that catch dirt and twigs. Real grass clumps for causes: tussocks of a bunch grass, a dandelion rosette, the ring of a cushion, the line of a joint. For us a clump is a cell of the community's own size and shape: a lawn's fine and even, a long-grass yard's tussocks half a metre across, heather's plants a hand to a forearm across. The clump's centre takes the field's value there. The direction a blade leans is a fact where one exists (the prevailing wind on an exposed slope, a mown lawn's stripe, a path's trampling), and seeded texture otherwise.

### How grass hands over to the ground

The sources agree on three steps, and Tsushima does all three (secondary).

1. **The blades take the ground's colour at their root and the ground's normal in their light.** Frostbite blends the grass colour with the terrain's and lights it with the terrain's normal. AMD bends normals a quarter of the way up. Tsushima blends normals towards the terrain's with distance.
2. **The ground takes the blades' colour before they go.** Tsushima's terrain takes the grass top's colour as the blades thin. Outerra's canopy draws the far land from the same field. BotW's grass colour map is tied to the terrain tile (secondary). Tiny Glade's "astroturf" popping through is what happens when the two do not agree.
3. **The edge is hidden.** Thinning with widened survivors (AMD, Outerra), a blend of shape before each switch (Tsushima), the land's own relief, and fog.

What none of them published is how the far colour is chosen. We can do better than an artist's guess: render a square metre of each community's near tier, at full detail, from several elevations in grey light, and store its mean colour, value and gloss by elevation and season. Seen along the ground at the street stop, a lawn shows the sides of its blades; seen from the near-isometric view, it shows their tips and the dark between them. The ground shader then draws exactly what the strokes average to at that angle, so the hand-over has nothing to show. It is the performance study's rule (the same stones at every tier) applied to plants.

### Painterly grass that reads as masses

Masses come from shared normals and value, not from blades. The film studios found that per-leaf lighting gives "unappealing visual noise" and lit canopies by aggregate normals (Peterson and Lee, SIGGRAPH 2006); our birches proved the same thing in the corner (`docs/experiments.md`, LT1, trees: value from the masses, never the cards). For grass that means:

- a tuft's strokes take one normal, from a small dome over the tuft blended with the ground's; the lit top of a tussock and its shaded underside are one shape;
- colour runs root to tip along each stroke, the root taking the ground's colour (Frostbite, BotW) and the tip the community's top colour for the season;
- the dark between tufts is occlusion, the light's, never a darker pigment (rule 1, SEASON's lesson);
- seeded variation is in hue within a clump, not in value between neighbours, as the birch's turned leaves were fixed (`docs/experiments.md`: a rust at four fifths of the gold's value);
- light through the blades against a low sun is the wrapped back term the leaves already use, so a backlit field glows in October at 16:00;
- wind shows as a travelling change of value: blades bent by a gust show their sides, so a gust crossing a yard or the heath is a lighter band (`docs/research/animation-and-motion.md`, nature in motion). From the street stop up that reads better than movement, and the ground shader can draw it too, so the far heath ripples with the near.

Kazuo Oga's method points the same way: a base laid wet in one go, refined once dry, about 21 colours, to "get the essential point across" (Animation Obsessive on Oga, secondary). No published Ghibli source describes a grass field as dark base, lit tops and a few accent strokes; that is our reading of the paintings, not their doctrine.

## 2. Plants on hard surfaces

### How the craft places them

No shipped game we found grows plants on stone from causes over time. The craft splits three ways.

- **By hand, with a rule of thumb.** Naughty Dog's artists on The Last of Us Part II asked whether water, light and soil would carry growth before placing it, instead of scattering it everywhere (Vaccaro on 80.lv, secondary). Uncharted 4 gave moss its own shading: lighter at the tips, fuzz seen only at a grazing angle, wrapped light, and colour put back into its deep occlusion (Brinck and Maximov, SIGGRAPH 2016, as read for `history-in-things.md`).
- **By masks from the shape.** Houdini's Measure node gives curvature, its sign telling a concave joint from a convex arris; Unreal's PCG has nodes for density from the normal, distance to other points, density filters and self-pruning. That is accessibility (Miller 1994) and exposure (Hsu and Wong 1995): every crevice gets the same moss.
- **By transport.** γ-ton tracing (Chen et al., SIGGRAPH 2005) shoots ageing particles from sources (rain, a leaking pipe, the sky), lets them fly, bounce or flow along the surface and settle, carrying humidity and moss seed. Its teaser is our case: the gaps between tiles gather the water that runs off the raised faces and grow moss, and moss once there traps more. It iterates, so growth has a history, not just a final state.

We already have the transport. `water.py` bakes where rain lands, runs, drips and lingers; `growth.py` turns damp, traffic and years into moss and lichen; the sky map says how much sky each point sees. What is missing is thick growth: the tuft in the joint, the cushion on the coping, the fern in the wall. They are the same potentials drawn as instances, at places the generator already knows. Every joint line, wall foot, coping top, nosing, gutter and roof course is a curve or a face the stone and house generators make. So plants on hard surfaces are placed along those lines and faces, sampled at a spacing. Each candidate has a seeded rank and is kept where the potential beats it.

### What the facts say about where

| Place | What grows | What decides it | Source |
| --- | --- | --- | --- |
| Paving joints, trodden | annual meadow-grass and procumbent pearlwort, in mats; pearlwort roots at its nodes and spreads on shoes | trampling it tolerates; sweeping and herbicide | NVC OV20 (secondary); *Sagina procumbens* (secondary) |
| Joints, dry, sunny, nitrogen-rich | silver moss (*Bryum argenteum*), under a centimetre tall; silver when dry, green when wet | drought it tolerates; dogs and road edges | *Bryum argenteum* (secondary) |
| Joints, damp and shaded | pearlwort with silver moss cushions | water and sky | Sagino-Bryetum (unverified) |
| A kept street as a whole | about 1.4% mean weed cover in five north-European towns after a year without herbicide, highest (about 2%) along the edge away from the road; most cover where herbicide rules were strictest | care and the building edge | Melander et al. 2009 (abstract) |
| Wall tops, old mortar, roof tiles | *Grimmia* cushions 1 to 2 cm tall; *Tortula muralis* under 1 cm, the commonest moss on mortared walls | lime, exposure, years | (secondary) |
| Moss cushions | *Grimmia* cushions 11 to 57 mm across; small ones near hemispheres, big ones flatter; the smallest dry in an hour, the biggest stay wet for a day or more | size and the hours since rain | Zotz et al. 2000 |
| Lime-mortared walls | wall-rue, "almost exclusively" in lime mortar, half-shaded and damp; scarce on acid rock; rarer in polluted towns | the mortar's chemistry, a dated fact | BSBI account of *Asplenium ruta-muraria* |
| Roofs | moss on north slopes, low pitches, under trees, where leaves lie; none in the strip below zinc or copper flashings | aspect, pitch, shade, care | Marley (roof-tile maker) |
| Gutters | birch seedlings where a seeding birch stands within about 60 m and the gutter's litter is left wet through a seed fall (August to December); good seed years every three or four | the trees, care | Forestry Commission note 54 for the birch's seed (a gutter as a site is our inference) |

Three rules follow, each a function of fields we have.

1. **Joint growth is sparse and lies at the quiet edge.** `joint plants = potential(water, sky, soil in the joint) × years since laid or swept × (1 − busy) × (1 − care's weeding)`, peaked at the building side and the wall's foot. A kept street of 1989 stays at a percent or two. A lane nobody has swept since a shop closed greens up within a summer: annual meadow-grass flowers about six weeks after it germinates and sheds seed eight months of the year (secondary). This is the history budget's rule seen from the botany: the quiet edge is one green band, the walking line none.
2. **The species follow the stress.** Trodden joints get meadow-grass and pearlwort only; dry sunny joints silver moss; shaded wet joints moss cushions; the less-trodden edge dandelion rosettes. Silver moss and the cushions change with the hours since rain (silver to green, grey to dark), which the water layer already knows.
3. **A fern in a wall is a fact about its mortar.** Wall-rue only on lime-mortared walls; repointing in cement (a dated work in `upkeep.py`) ends it. The corner's phyllite drystone walls carry none; an old lime-mortared house plinth may.

## 3. Bushes, hedges, climbers and gardens

### Bushes as masses

A bush is a small tree, and the trees' method holds: a few faceted masses per species and age, sprays taking their normals from their mass, value from the masses (`docs/trees.md`). The film precedent is aggregate normals (Peterson and Lee 2006). The games' version, normals copied from a hull onto the cards, is standard craft, but we could not open a source for it (unverified). What changes on the M4 is how the sprays are drawn. A bush at eye level is one to three metres away, where a leaf is 15 to 90 pixels across (ours). So its near tier is real leaves as opaque geometry, and its cards for the street stop and beyond sit on an opaque core, as the trees' should (section 7).

### Hedges: clipped and let go

A clipped hedge is a made form, and it should be built as one. It has an opaque hull (its batter, its top's camber, its height), a leafy skin painted at our scale with relief, and short opaque shoots standing out of it, as long as the growth since the last cut. The facts give the rest.

- Norway's hedges are trees or shrubs clipped every year (SNL, "hekk"). Tall ones are spruce, yew, thuja, lime, hawthorn or hornbeam; low ones currant, spiraea, privet, box or *Rosa rugosa*. They are planted two to five a metre, and a young deciduous hedge is allowed 15 to 30 cm more height a year. Deciduous hedges are cut February to April with one or two summer cuts, thuja and yew July to August.
- Trims a year by species: box and privet two or three, yew, hawthorn and thuja two, beech and hornbeam one (RHS).
- Neglect (RHS): beech, hornbeam, hawthorn, box, holly and yew can be cut back hard and recover. Most conifers cannot reshoot from old wood, so an overgrown thuja hedge is kept tall or replaced. A hard renovation shows one side cut in a year, the other the next, the top in the third.

So a hedge's look at a date is its hull plus the shoots grown since its last cut, from its species' rate and its keeper's calendar. A hedge in July before its summer cut is shaggy; in September it is crisp. A hedge whose clipping stopped in 1979 has grown out by ten years of shoots and is drawn as a bush mass. A thuja hedge that cannot be cut back is a fact the town carries for decades. How many years an unclipped hedge takes to lose its shape was not found; two or three seasons is our estimate.

### Climbers on walls

The craft is an old one. Thomas Luft's Ivy Generator (2007) grows a vine by five weighted pulls (80.lv, secondary): its own direction, a random one, adhesion to the nearest surface, up towards the light, and gravity. Blender's IvyGen is built on it. Space colonisation (Runions et al. 2007) grows towards attraction points in an envelope and fits the pipe model. Tiny Glade's ivy grows over walls but not windows and was taught to leave arches. For us the envelope is the wall's face minus what its keeper keeps clear, and the attraction points are placed by light and damp.

The facts that decide whether a wall has a climber at all:

- Ivy is native on this coast, wild from the Oslofjord to Bergen, climbing rock, walls and trunks by aerial roots (SNL, "bergflette"). It can cover a two-storey house in 15 to 20 years (RHS). It cannot bore into sound masonry, but it widens cracks, gets into gutters and lifts slates. It is cut back about once a year, and pulled off it leaves root hairs on the wall. Measured on test walls, it took two years to establish and three more to reach 2 m (Coombes et al. 2018).
- The common Norwegian *villvin* (*Parthenocissus inserta*) has no adhesive pads and needs support; *klatrevillvin* (*P. quinquefolia*) has pads and is used on brick walls (SNL). *Villvin* turns red in autumn; both are bare in winter.
- Old Norwegian timber cladding is kept clear of shrubs so the wall can dry; rot starts low, at splash and soil (Bygg og bevar).

So on the town's painted timber a climber is rare and always a fact: a household's choice on a trellis, or a neglected wall. On stone, brick and render it is common, and its edge is the keeper's: a band cut clear round windows, gutters and eaves as wide as the care. A wall stripped of ivy keeps its rootlet scars for years, which the growth layer can draw. At the street stop ivy reads as one dark mass with a lit ragged edge; near, its leaves (5 to 8 cm) are opaque geometry.

### Gardens are a household's facts

We found no shipped game that grows gardens from a household's history. Townscaper is the nearest rule system (Stålberg, secondary). Its garden pieces fit only enclosed, flat ground, and their only edge is a wall. Small walls appear where houses change colour, so the gardens read as separate plots. Tiny Glade lets players paint flowers into the meadow.

For us a garden is the yard's record (`docs/living-fabric.md`). It holds the keepers and their care by decade, and what each planted and when: a lilac in 1931, the lawn in 1962, a thuja hedge in 1974. It also holds the era's shelf of plants from the setting pack, and the yard's uses (a washing line, a car's hard standing). The layout (beds along the sunny wall and the path, the lawn in the middle, currants and rhubarb at the back) is the pack's rule per era. It is still to be checked against period photographs (`docs/research/vegetation.md`). Lilac and *Rosa rugosa* both spread by suckers into thickets (SNL), so an old garden's shrubs widen with the years, and an abandoned one's widen faster.

## 4. Fallen leaves and litter

Games draw fallen leaves as decals or as instanced leaf meshes over a seasonal mask, and blow some about as particles. Ghost of Tsushima kept up to 60,000 leaf particles in a scene, from one system following the camera (`docs/research/trees.md`, `vegetation.md`). We found no game that moves a season's leaves from where they fell to where they lie.

The facts give a small model.

- **Where they come from.** Each tree drops by its species' phenology and its seeded ranks (`docs/trees.md`, seasons). In Norway shortening days start leaf fall, and trees by street lamps can keep their leaves longer (SNL, "løvfall"). So the deposit starts under and downwind of each crown, in the order its own leaves go.
- **Where they go.** Dry leaves move in a fresh breeze. Beaufort's force 4 lifts dust and loose paper (secondary), and we take it as the threshold for dry leaves on the ground (ours). Wet leaves stay. Moving leaves settle where the air slows: the lee of walls and fences, inside corners, kerbs, steps' risers, gutters. A snow fence drops its load on its lee side in the same way (secondary). That is γ-ton's settle state again: low accessibility traps what moves.
- **What clears them.** Feet, and wet leaves trodden flat go dark and slick, compacted "much like black ice" (Network Rail). Sweeping and raking by the keeper, on dry days (RHS). Mowing shreds them on a lawn (RHS).
- **How they age.** Most leaves take about two years to become leaf mould in a heap; oak and beech break down easily, thick sycamore and horse chestnut slowly (RHS). On paving the change from gold to brown to black over the weeks was not found (unverified).

So the leaves of 20 October 1989 are a deposit field per chunk, computed for the date from the autumn's days so far. Each day's fall from every tree is moved by that day's wind from the one wind field and settled in the lee. The feet field clears the walking line and each keeper sweeps their own ground; days since fall and rain darken what is left. The daily weather is a hash of the world's seed and the day (`docs/research/nature.md`), so the same date always gives the same leaves. From the street stop up the ground shader draws the deposit as colour and value. Within about 8 m each leaf is an opaque instance, two triangles with a fold, coloured by its tree and its age. That is the history budget's own example: leaves gather where feet do not go (`docs/living-fabric.md`).

Litter rides the same field with other sources: cigarette ends by the café's tables and door, paper where the wind leaves it, a poster's torn strips at the foot of the boards. Each source is a use with a place and hours, and each is swept by its keeper.

## 5. Our fields acting on plants

Every cause that acts on a plant already has a home (`docs/foundations.md`, one home per system; `docs/living-fabric.md`, the fields). Here is what each does to ground cover.

| Field or clock | What it does to plants | Rule and source |
| --- | --- | --- |
| Feet | wears a path into turf and heath, clears joints and leaves from the walking line | Helbing's active walker model (Nature 1997): ground comfort rises with each footprint and recovers over a time T per community; about 15 passes make a visible trail (secondary). Grasses and rosette plants recover once use stops, while low woody plants such as heather do not recover significantly (Pescott and Stewart 2014, a meta-analysis of 188 trials); on subalpine heath, grasses came back in about two years and mosses not within three (`docs/research/nature.md`). So a lawn's path heals in a year or two (ours), a heath's path lasts years, and moss keeps a scuff longest |
| Water and damp | where moss, rushes, moss cushions and joint plants grow; how long cushions stay dark | `water.py`, the land's wetness index; Zotz 2000 for drying |
| Sky and sun | shade-tolerant against sun-loving species; moss on north faces; lichen on lit dry ones | the sky map, a sun-dose bake |
| Soil depth | bare rock, heath mat, turf, trees; the turf's lip over rock | the land's regolith (`land-rock-and-water.md`) |
| Wind and salt | the heath's wind-cut edge, low tough plants on the exposed shore, the lean of grass; and the one wind field moves every blade, leaf and spray | the wind field calibrated on Beaufort: sprays wake at force 2, branches at 4 (`animation-and-motion.md`); grass at 2 to 3 (ours) |
| Care | mowing, clipping, weeding, sweeping, cutting back: each a calendar with a keeper | lawns cut weekly or fortnightly March to October at 13 to 25 mm, never more than a third at once, and a lawn left goes loose and yellow at its first cut (RHS); hedges by species (SNL, RHS) |
| Vacancy | a household gone: its care falls to zero | the yard's succession: closed turf resists birch for years; disturbed ground takes fireweed, at its peak about five years after the disturbance (secondary), then birch near a seed source (Forestry Commission note 54) |
| The season | colour, flowers, seed heads, leaf fall, dieback | each instance's seeded rank against its species' phenology (SpeedTree's model, `docs/research/trees.md`); the pack's calendar, shifted by exposure and the town's warmth |
| Years since bare | how far a joint, a coping, a roof has greened | `growth.py` already, for films; the same for tufts and cushions |

Two clocks matter most for the screen. Mowing stopped turns a lawn into long grass in weeks: about three missed cuts, by the one-third rule (ours). Long grass left a year shows straw seed heads over green in October, the strongest sign of neglect a yard can show from the city camera. Succession then turns long grass into willowherb and birch over years. That is D's yard since 1986: three summers of long grass, willowherb and the first birch seedlings, the path to the door grassing over (`docs/experiments.md`, LT1).

## 6. Cost on our machine

### What a pixel holds for plants

At 2560 by 1440 with a 35 mm lens a pixel covers about 0.48 mm per metre of distance (`performance-at-scale.md`). The plants' own sizes, in pixels across (ours):

| Thing | Size | 1 m | 3 m | 8 m | 20 m | 40 m |
| --- | --- | --- | --- | --- | --- | --- |
| A grass blade | 4 mm | 8 | 3 | 1 | 0.4 | 0.2 |
| A painted stroke (a few blades) | 15 mm | 31 | 10 | 4 | 1.6 | 0.8 |
| A moss cushion | 30 mm | 63 | 21 | 8 | 3 | 1.6 |
| A birch leaf | 45 mm | 94 | 31 | 12 | 5 | 2.3 |
| An ivy leaf | 70 mm | 146 | 49 | 18 | 7 | 3.6 |
| A tuft of long grass | 300 mm | 625 | 208 | 78 | 31 | 16 |

The performance study's rule is a median visible triangle of ten pixels or more. So each kind's geometry ends where its parts drop below about ten pixels. Single leaves and cushions end at about 8 m, strokes at 4 to 8 m unless widened, tufts as single shapes at 40 m or more. Past those distances each is carried by the next thing up: a spray card, a tuft, the mat, the ground's colour.

### Opaque against alpha-tested on a tile-based GPU

Apple's own guidance is plain (WWDC 2020, sessions 10602 and 10632). Its GPUs keep "the frontmost visible layer for each pixel" and shade only that, and opaque fragments let this hidden-surface removal "eliminate the most work". A shader that can discard makes feedback fragments, and "Alpha tested foliage falls into this category". The GPU must run them to know what they hide, and after a discard it must "go back to HSR". Apple asks for opaque draws first, then alpha-tested, then translucent, never interleaved. When hidden-surface removal works fully it rejects hidden fragments as well as a depth pre-pass does, at no extra cost. Unity's AlphaTest queue already draws our leaves after the opaque town.

What follows for us:

- **Ground cover near the camera is opaque.** A meadow of opaque strokes costs its vertices and its front layer; the same meadow of cards costs every card in every layer.
- **Cards are only where few overlap,** and each is cut to its painting's outline. In Humus's measurement on a smoke puff, a polygon of six to eight vertices fitted round the alpha cut the area to 52 to 60% of the quad. A spray's outline should do as well (unverified for our atlas).
- **An opaque core hides what lies behind it.** Anything opaque drawn first lets the hardware skip every card behind it.
- **A depth pass for alpha-tested leaves is worth a test.** A cheap first pass only samples the atlas and discards. The full shading follows with an equal depth test and no discard, so each leaf pixel is shaded once. It costs a second pass through the tiler, so the harness decides (ours; Apple's talks do not cover it).

### Edges: MSAA, alpha-to-coverage, hashed alpha

MSAA is cheap on Apple GPUs: samples live in tile memory and resolve there, so the multisampled target can be memoryless (WWDC 2020). Alpha-to-coverage needs MSAA and gives smooth cut-out edges; our leaves use it now. Hashed alpha testing (Wyman and McGuire 2017) keeps thin cut-outs from vanishing with distance; its noise is meant to be smoothed by temporal antialiasing, which we do not use (`docs/research/trees.md`). Coverage-preserving mips (Castaño, for The Witness) keep a card's coverage at every mip, and `ArtImport.cs` already sets them for the birches. With MSAA kept, the trees' and any cards' edges are alpha-to-coverage with coverage-preserving mips. Whether alpha-to-coverage counts as feedback for Apple's hidden-surface removal is not stated in what we read; it is safest to assume it does (unverified).

### Dense geometry and the tiler

Opaque geometry still costs on a tile-based GPU. Every vertex is transformed and binned before any pixel is shaded. The binned vertices go into a tiled vertex buffer that "may cause a Partial Render if full" (WWDC 2020, 10602), flushing the tiles mid-frame at a cost in bandwidth. Thin triangles also waste shading on the 2×2 blocks at their edges. So ground cover has a triangle budget rather than a fill budget, and its strokes stay wide enough to keep the median triangle near ten pixels. We propose a provisional split of the frame's 2 million visible triangles, to be measured. Ground cover's near tier gets up to about 300,000. The tree nearest the camera gets up to about 150,000 when it has real leaves. The rest is the town's.

### Shadows

No game we read casts real shadows from its grass. Ghost of Tsushima fakes them with raised terrain and screen-space shadows (secondary); Book of the Dead stops small plants casting at about 15 m. Ours: tufts, strokes, litter and cushions never cast; they receive the sun's shadow and carry their own occlusion from the tuft's depth, baked. Bushes and hedges cast through their opaque hull or core, as the trees cast through proxies (`performance-at-scale.md`). Screen-space occlusion takes a small share on blades, as it does on wood, or its halo grows round every stroke.

### Impostors and fill

An impostor is one alpha-tested layer per tree, far cheaper in fill than a crown of cards. Still, one Unity user saw frame time rise from 6.4 to 7.3 ms when 3,000 plants became impostors (`performance-at-scale.md`, secondary). Impostors are for trees past about 200 m. Bushes and hedges past the street tier become part of the ground's colour and the land's merged mesh.

### GPU placement in Unity 6 URP

- **Compute plus indirect draws.** A compute pass per tile reads the field tiles and generates candidates on a jittered grid, with a hashed seed per cell. It keeps each candidate whose rank the potential beats (Frostbite's roulette), culls by distance and frustum, picks a level by pixel size, and appends instances and indirect arguments. `Graphics.RenderPrimitivesIndexedIndirect` then draws them (Unity scripting reference). It "only works on platforms that support" compute shaders; its `RenderParams.worldBounds` is used "to cull and sort" the draw; with no camera set it renders for every camera. The shader reads its instance from a structured buffer through Unity's indirect helpers.
- **No geometry shaders on Metal** (Unity manual). Many stylised Unity grass tutorials build blades in a geometry shader; none of them will run on the M4.
- **BatchRendererGroup** suits things that live as stable records and change by events: moss cushions on a known coping, hedges' hulls, garden plants. Its culling runs on the CPU, so it is not for millions of grass strokes. Plants with records (bushes, hedges, climbers) can also be GameObjects through the GPU Resident Drawer once their shaders are DOTS-instanced, with their facts through `unity_RendererUserValue` (`performance-at-scale.md`).
- **Determinism.** Each candidate's seed is a hash of its tile, cell and layer, never a running random stream. A candidate present at density 0.3 is still there at 0.5, and nothing reshuffles when a field changes: Horizon's "locally stable", and our trees' seasonal ranks.

For scale, a mobile URP sample draws grass with one indirect draw after a compute frustum cull. It reports 10 million instances at 50 to 60 fps on a 2019 mid-range Android phone, without stating its blade or how many are visible (Colin Leung's MobileDrawMeshInstancedIndirect example).

## 7. What changes for the trees

The trees' design (`docs/trees.md`) holds: a timeline read at a date, hand-made parts, crowns shaded as masses, seasons by rank, one wind field. Its rendering was chosen before the M4 was the reference machine, and that part changes.

1. **Measure the crowns first.** A 60-year birch has up to 4,200 cards a metre or so across, turned to the eye, so each shows its whole area from every view. Over a crown of about 80 m² seen side on, that is of the order of fifty card layers a pixel, every one a feedback fragment. This is our estimate from `PARTS` in `tree.py`; the real figure depends on the cards' coverage and the view. Before anything else here is built, the harness should report the corner's frame time with the birches on and off, with an overdraw capture of one crown in Xcode's Metal debugger.
2. **Cards cut to their outline.** Each cell of the cluster atlas gets a six- to eight-sided hull fitted to its alpha (Humus's method), carried by the card through `_OS_FACING`. That is about half the fill, with no change to the look.
3. **An opaque core in every mass.** The crown's masses already exist as faceted volumes (`docs/trees.md`, step 3). Each is shrunk by the depth of the card layer and drawn opaque, in the shade value of the mass's interior, so it hides the cards behind it. It is the trees research's "density shells", used here for the hidden-surface removal. Its strength follows the season: full in leaf, gone as the crown thins, absent when bare.
4. **Real leaves near.** The visual direction asks for real leaves where cards would turn as you pass. On the M4 that is affordable only as opaque geometry, and only where a leaf is ten pixels or more: within about 8 m. The crown is chunked by lobe, each about 2 to 3.6 m across. A lobe within 8 m draws its sprays as modelled leaves, two triangles each with a fold along the midrib, four close in; beyond, it draws its cards. MSAA smooths the leaves' edges, as it does any geometry. The atlas already gives every leaf an id and a rank, so a leaf that has fallen from a card has fallen from the mesh too. Standing under the corner birch at eye level, perhaps 1,000 sprays of 30 leaves are near: about 100,000 to 150,000 triangles (ours). The foundations' near budget of 60,000 for a tree is too low for the tree one stands under; the harness should set it.
5. **Fewer, larger cards further off.** The alpha cutoff falls with distance, as Firewatch's did, so a far crown fills and reads as paint while its layers drop. Octahedral impostors follow past about 200 m, as planned.
6. **Shaders ready for instancing.** `Tree.shader` moves to target 4.5 with DOTS instancing and LOD cross-fade, as the performance study already asks.

None of this touches the trees' facts, rules, style or the review findings recorded in `docs/experiments.md`; it is the porting the plan expects.

## 8. One system for ground cover and plants

### Five kinds, one set of fields

| Kind | What | Built as | Near (to 8 m) | Street (8 to 40 m) | City and far |
| --- | --- | --- | --- | --- | --- |
| Films | lichen, algae, thin moss, the silver of dry moss | `Growth.hlsl` on every surface | full marks (`OS_Near`) | the film | the film's mean in the bakes |
| Mats | lawn, moss mats, heath, crowberry, bog, a bed's soil | a surface lying on the ground, its height the community's (2 cm for a lawn to 40 cm for heather), with a crisp edge where its field crosses a threshold, painted at our scale with relief; part of the land's chunk mesh | the mat with its edge as geometry | the same, simpler | the ground's colour by community and season |
| Tufts and strokes | grass, weeds in joints, heather sprigs, flowers, seed heads, litter near | GPU instances from the fields, opaque strokes | full density | thinned, survivors widened, gone by 20 to 40 m | none: the mat's shader carries their mean |
| Plants | ferns, bushes, hedges, climbers, garden plants, young trees | things with records, built like small trees from hand-made modules: masses, sprays, an opaque core | real leaves | cards on the core | merged into the land, or impostors for big ones |
| Litter | fallen leaves, needles, twigs, cigarette ends, paper | a deposit field per chunk for the date | opaque instances | the field in the ground's shader | the field's mean |

The mats are the piece the games do not name and our style needs. "Ground cover in clusters with edges, never noise" (`docs/visual-direction.md`) is a geometric statement. It means a lawn's edge against a worn path, the heath's lip over bare rock (`land-rock-and-water.md`), a moss mat's rim on a ledge. A mat as a surface of its own keeps that edge as a silhouette at every tier, for a few triangles a metre, and near the camera the tufts stand on it. It is the same split as the stone: real edges where they read, painted surface between.

### One placer

Every instance in the system comes from one rule, the one the lichen and the leaves already follow:

`present = potential(fields, facts, date) > rank(seed)`

The potential comes from three places: the fields (feet, water, sky, soil, wind and salt), the facts (the community, the keeper's care, the years since bare, mown or cut, the season), and the species' table in the setting pack. The rank is the candidate's seeded number, fixed for ever. Time and care move the potential; nothing moves the ranks. So the same tuft stands in the same place at every visit, a yard in 1988 contains its 1987, and a change to one field changes only what reads it. The pack brings the species, their communities and their tables: viability per field, response to each kind of care, phenology, and the stroke and spray parts. The system knows no country.

### What the ground and every part must carry

This is the input to `docs/building-blocks.md`.

| Carrier | Must carry | Why |
| --- | --- | --- |
| The ground, per chunk (field tiles) | soil depth, water and wetness, sky and sun dose, feet, wind and salt, substrate (rock, soil, fill, paving), the community and its years since disturbance, the keeper and care regime, the leaf and litter deposit for the date, the mat's height | every placer and the ground shader read the same truth |
| The ground's shader | per community and season: its colour, value and gloss by view elevation, measured from its near tier; the wind's gust as value | the far colour is the near tier's own mean |
| Every hard part (stone, walls, paving, kerbs, roofs, gutters) | its joint lines and growth faces as data: a curve or face with width, depth, soil in it, water, feet, years since laid or swept, and its chemistry (lime or acid); a coping or ridge for cushions; a gutter run as a litter trap | tufts, cushions and ferns are placed on them, not scattered over them |
| Every wall face | its climbable region and material (masonry or painted timber), its keep-clear zones (windows, gutters, eaves, downpipes), trellis sockets | climbers grow inside a fact-made envelope |
| Every plant | a record (species, origin, born, keeper, events: planted, clipped, cut back, removed), parts by tier, wind data (element, pivot, stiffness, phase) as `animation-and-motion.md` sets out, season ranks per leaf or spray, an opaque core | a plant is a thing like a tree |
| Every instance (GPU buffer) | position, rotation, scale, part and species index, seed and rank, wind phase, the field tile it reads | the placer's output; nothing else is stored |

### Order of build

The ground cover rides on the land's fields (`land-rock-and-water.md`, what we should do, item 5) and on the performance harness. Mats come with the ground shader; tufts with the placer; plants one species at a time, each judged alone, as the trees were.

## 9. Look tests that would prove it

Each from eye level, the street stop, 12 m and the near-isometric view, in grey drizzle, the 16:00 low sun and the blue hour, in colour, greyscale and at one-eighth, with frame time on the M4.

1. **Strokes against cards against ground only.** One square metre each of lawn, long grass and heath, built three ways, judged in grey light first. *Proves:* how near ground cover is built, on the look and on the frame. *Pass:* strokes read as painted masses from eye level and do not shimmer at the street stop; the frame is within the ground cover's share.
2. **The hand-over strip.** D's yard and the heath above E, 60 m deep, with the near tier switched on band by band, and the far colour measured from the near tier by elevation. *Pass:* a reader shown the frames at one-eighth names no seam; the mean colour across the band changes by less than a just-noticeable step (ΔE under about 2).
3. **D's yard through the years.** 1985 (mown), 1986, 1987, 1988, 1989 and 1995. *Pass:* cold readers order the years and say the yard was left, and about when.
4. **The joints of the gully steps and the landing.** 1960 (the ironmonger open), 1980 (shut six years), 1989 (the café a year old). *Pass:* readers find the walking line and the quiet edge; weed cover on the kept lane stays near Melander's percent or two.
5. **The birch's cost.** The corner birch five ways: cards as now, cut to outlines, with opaque cores, with a leaf depth pass, with real leaves near. Frame time and an overdraw capture for each, and the look sheet at eye level under the crown. *Pass:* the look holds and the corner's frame meets its budget.
6. **20 October 1989 at the landing.** Leaves in the lee of the wall and on the steps' quiet edge, swept from the café's doorstep and the walking line, dark where trodden wet. *Pass:* readers say where people walk from the leaves alone.
7. **The heath from the far stop.** Heath, lawn, long grass and rock as four clearly different values. *Pass:* the city camera reads the yard as gone wild and the hillside as heath at one-eighth.

## What we should do

Ranked by what each buys for its cost.

1. **Measure the birches on the M4** (half a day, once the harness exists). Buys the truth about the corner's dearest pixels before any re-fit.
2. **Cut the leaf cards to their outlines and add opaque cores to the crown masses** (two to three days). Buys about half the crowns' fill and the back half of each crown hidden for free, with no change to the look.
3. **The ground cover placer: compute plus indirect draws, the seeded rank rule, levels by pixel size** (about a week, on the land's fields). Buys every tuft, joint plant, flower and near leaf from one system, deterministic, near the camera only, no GameObjects.
4. **Mats and the ground shader by community and season** (about a week, with the land's ground shader). Buys the crisp edges our direction asks for at every tier, and the far ground that is the colour of what grows on it.
5. **Look test 1, strokes against cards against ground** (two to three days). Buys the decision on how near ground cover is built, judged in the engine.
6. **The far colour measured from the near tier** (two days). Buys a hand-over with nothing to show.
7. **Joint plants and cushions on the stone generators' joint lines** (three to four days). Buys the gully's quiet edge in tufts and cushions from the potentials it already bakes.
8. **The leaf deposit field and the corner's October** (three to four days). Buys the season's most legible history of feet and care.
9. **Real leaves near, per lobe** (about a week, after 1, 2 and 5). Buys the eye-level crown the visual direction asks for, on a measured budget.
10. **Hedges as hull plus growth since the last cut; climbers in a fact-made envelope** (about a week each, when the corner's houses and yards need them). Buys gardens and walls that show their keepers.

## For Øystein to decide

1. **Strokes or fine blades near the camera.** Strokes (a few blades as one painted mark) suit the style and the machine; fine blades are the photoreal standard. *Recommendation:* strokes, confirmed by look test 1.
2. **Real leaves near the camera at a cost.** The tree one stands under may need 100,000 to 150,000 triangles. *Recommendation:* yes, for eye level and scenes, within the budget the harness sets; cards elsewhere.
3. **Grass that parts round people.** A play and scope question (Tsushima's displacement buffer, Death Stranding's force fields). *Recommendation:* later, through the feet field when people walk the lanes; not before the corner.
4. **How green a kept town of 1989 is.** The facts say sparse: a percent or two of the joints in a kept lane, greenery at the quiet edges, yards and empty plots. *Recommendation:* true to the facts; the picturesque overgrowth belongs where a fact puts it.

## Gaps

- The web-search budget ran out part way. Not reached: Genshin Impact, Sable, Planet of Lana, Kingdom Come: Deliverance 2, The Witcher 3, the Witcher 4 demo's Nanite foliage, and The Last of Us Part II's overgrowth. Nor hedges in Hitman and Forza Horizon 4, or procedural gardens in The Sims and Cities: Skylines II.
- Too large to open: the Ghost of Tsushima grass slides, Horizon Zero Dawn's placement and vegetation slides, Uncharted 4's technical art. Their details here are secondary; reading the decks needs a download Øystein would approve.
- Whether alpha-to-coverage disables Apple's hidden-surface removal as discard does; the cost of a leaf depth pass on the M4; the birches' real overdraw. All for the harness.
- Facts not found: moss growth rates a year; leaf colour on the ground by week; leaf decomposition rates by species; when birch drops its leaves in Stavanger; how fast an unclipped hedge loses its shape. Stavanger's gardens of 1989 still need period photographs.
- No published source gives a painterly far colour for grass by view angle; ours is a method to test.

## Sources

Games and engines: [Procedural Grass in Ghost of Tsushima, GDC 2021](https://gdcvault.com/play/1027033/Advanced-Graphics-Summit-Procedural-Grass) (abstract) and write-ups [1](https://tigerabrodi.blog/grass-in-ghost-of-tsushima), [2](https://tigerabrodi.blog/what-we-can-learn-from-grass-in-ghost-of-tsushima-renders), [3](https://gist.ly/youtube-summarizer/procedural-grass-systems-in-ghost-of-tsushima-achieving-art-direction), [4](https://cainrademan.github.io/Unity-Grass/), [5](https://github.com/2Retr0/GodotGrass) (secondary) · [Samurai Landscapes, GDC 2021](https://gdcvault.com/play/1027352/Samurai-Landscapes-Building-and-Rendering) (abstract) · [GPU-based procedural placement in Horizon Zero Dawn](https://www.guerrilla-games.com/read/gpu-based-procedural-placement-in-horizon-zero-dawn) · [The vegetation of Horizon Zero Dawn, GDC 2018](https://gdcvault.com/play/1025066/Between-Tech-and-Art-The) (abstract) · [Adventures with deferred texturing in Horizon Forbidden West](https://www.guerrilla-games.com/read/adventures-with-deferred-texturing-in-horizon-forbidden-west) · [Terrain rendering in Frostbite, SIGGRAPH 2007](https://media.contentapi.ea.com/content/dam/eacom/frostbite/files/chapter5-andersson-terrain-rendering-in-frostbite.pdf) · [Outerra, procedural grass](https://outerra.blogspot.com/2012/05/procedural-grass-rendering.html) · [AMD, procedural grass with mesh shaders](https://gpuopen.com/learn/mesh_shaders/mesh_shaders-procedural_grass_rendering/) · [AMD, work graphs and mesh nodes](https://gpuopen.com/learn/work_graphs_mesh_nodes/work_graphs_mesh_nodes-procedural_generation/) · [GPU Gems 1, ch. 7](https://developer.nvidia.com/gpugems/gpugems/part-i-natural-effects/chapter-7-rendering-countless-blades-waving-grass) · [GPU Gems 3, ch. 16, Crysis](https://developer.nvidia.com/gpugems/gpugems3/part-iii-rendering/chapter-16-vegetation-procedural-animation-and-shading-crysis) · [BotW terrain format](https://zeldamods.org/wiki/Terrain) and [technical analysis thread](https://www.resetera.com/threads/zelda-breath-of-the-wild-the-technical-analysis.8197/) (secondary) · [Making the World of Firewatch, GDC 2016](https://media.gdcvault.com/gdc2016/Presentations/Ng_Jane_MakingTheWorld.pdf) · [Campo Santo Q&A](https://blog.camposanto.com/post/102893584324/i-asked-twitter-if-anyone-had-questions-about-the) · [Tiny Glade developer posts](https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=2198150&count=200&maxlength=0) and [store page](https://store.steampowered.com/app/2198150/Tiny_Glade/) · [Book of the Dead: wind, scene building and optimisation](https://unity.com/blog/technology/book-of-the-dead-quixel-wind-scene-building-and-content-optimization-tricks) · [Time Ghost](https://unity.com/demos/time-ghost) · [Unity terrain grass and details](https://docs.unity3d.com/6000.0/Documentation/Manual/terrain-Grass.html) · [Unity terrain settings](https://docs.unity3d.com/6000.0/Documentation/Manual/terrain-OtherSettings.html) · [Nanite](https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-virtualized-geometry-in-unreal-engine) · [Unreal PCG node reference](https://dev.epicgames.com/documentation/en-us/unreal-engine/procedural-content-generation-framework-node-reference-in-unreal-engine) · [Death Stranding frame study](https://mamoniem.com/behind-the-pretty-frames-death-stranding/) (secondary) · [RDR2 graphics study](https://imgeself.github.io/posts/2020-06-19-graphics-study-rdr2/) (secondary) · [How Northlight makes Alan Wake 2 shine](https://www.remedygames.com/article/how-northlight-makes-alan-wake-2-shine) · [Interactive wind and vegetation in God of War, GDC 2019](https://gdcvault.com/play/1026036/Interactive-Wind-and-Vegetation-in) (abstract) · [Broken Roads vegetation](https://www.brokenroadsgame.com/dev-blog/vegetation-blog) · [How Townscaper works](https://www.gamedeveloper.com/game-platforms/how-townscaper-works-a-story-four-games-in-the-making) (secondary) · [Animal Crossing animal tracks](https://nookipedia.com/wiki/Animal_track) (would not open; unverified) · [The Art of The Witness, GDC 2014](https://www.artofluis.com/wp-content/uploads/2014/03/gdc2014_luisantonio_theartofthewitness.pdf) · [How Naughty Dog created the world of The Last of Us Part II](https://80.lv/articles/how-naughty-dog-created-the-immersive-world-of-the-last-of-us-part-ii/) (secondary) · [The Technical Art of Uncharted 4, SIGGRAPH 2016](https://advances.realtimerendering.com/other/2016/naughty_dog/index.html) · [Kazuo Oga](https://animationobsessive.substack.com/p/what-kazuo-oga-thinks-about-when) (secondary)

Rendering and the machine: [Optimize Metal performance for Apple silicon Macs, WWDC 2020](https://developer.apple.com/videos/play/wwdc2020/10632/) · [Harness Apple GPUs with Metal, WWDC 2020](https://developer.apple.com/videos/play/wwdc2020/10602/) · [Tailor your apps for Apple GPUs and TBDR](https://developer.apple.com/documentation/metal/tailor-your-apps-for-apple-gpus-and-tile-based-deferred-rendering) · [Computing alpha mipmaps (Castaño)](https://ludicon.com/castano/blog/articles/computing-alpha-mipmaps/) · [Hashed alpha testing (Wyman and McGuire)](https://research.nvidia.com/labs/rtr/publication/wyman2017hashed/) · [Particle trimming (Humus)](http://www.humus.name/index.php?page=News&ID=266) · [Simplified tree lighting using aggregate normals](https://history.siggraph.org/learning/simplified-tree-lighting-using-aggregate-normals-by-peterson-and-lee) · [Graphics.RenderPrimitivesIndexedIndirect](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Graphics.RenderPrimitivesIndexedIndirect.html) · [RenderParams](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/RenderParams.html) · [Metal in Unity](https://docs.unity3d.com/6000.0/Documentation/Manual/metal-requirements-and-compatibility.html) · [GPU Resident Drawer](https://docs.unity3d.com/6000.0/Documentation/Manual/urp/gpu-resident-drawer.html) · [MobileDrawMeshInstancedIndirect example](https://github.com/ColinLeung-NiloCat/UnityURP-MobileDrawMeshInstancedIndirectExample)

Growth on surfaces, climbers and placement: [γ-ton tracing (Chen et al. 2005)](https://ttwong12.github.io/papers/gammaton/gammaton.pdf) · [Houdini Measure](https://www.sidefx.com/docs/houdini/nodes/sop/measure.html) · [Space colonisation (Runions et al. 2007)](http://algorithmicbotany.org/papers/colonization.egwnp2007.pdf) · [Luft's Ivy Generator](https://80.lv/articles/an-ivy-generator-by-thomas-luft/) (secondary) · [Weed occurrence on pavements in five north-European towns](https://research.slu.se/en/publications/weed-occurrence-on-pavements-in-five-north-european-towns/) · [NVC OV20](https://en.wikipedia.org/wiki/British_NVC_community_OV20), [Sagina procumbens](https://en.wikipedia.org/wiki/Sagina_procumbens), [Poa annua](https://en.wikipedia.org/wiki/Poa_annua), [Bryum argenteum](https://en.wikipedia.org/wiki/Bryum_argenteum), [Tortula muralis](https://en.wikipedia.org/wiki/Tortula_muralis), [Grimmia pulvinata](https://en.wikipedia.org/wiki/Grimmia_pulvinata) (secondary) · [Water relations of Grimmia cushions (Zotz et al. 2000)](https://jetzlab.yale.edu/sites/default/files/files/WaterRelations2000.pdf) · [Wall-rue, BSBI](https://bsbi.org/in-your-area/local-botany/co-fermanagh/fermanagh-species-accounts/asplenium-ruta-muraria-l) · [Moss on roofs, Marley](https://cm.marley.co.uk/blog/how-do-i-remove-moss-or-lichen-from-my-roof) · [Birch regeneration, Forestry Commission note 54](https://cdn.forestresearch.gov.uk/2004/01/fcin054.pdf) · SNL: [bergflette](https://snl.no/bergflette), [villvin](https://snl.no/villvin), [klatrevillvin](https://snl.no/klatrevillvin), [hekk](https://snl.no/hekk), [syrin](https://snl.no/syrin), [rynkerose](https://snl.no/rynkerose), [løvfall](https://snl.no/l%C3%B8vfall), [geitrams](https://snl.no/geitrams) · RHS: [ivy on buildings](https://www.rhs.org.uk/prevention-protection/ivy-on-buildings), [when to prune hedges](https://www.rhs.org.uk/plants/types/hedges/when-to-prune), [hedge renovation](https://www.rhs.org.uk/plants/types/hedges/renovation), [mowing](https://www.rhs.org.uk/lawns/mowing), [leaf mould](https://www.rhs.org.uk/soil-composts-mulches/leaf-mould) · [Ivy on test walls (Coombes et al. 2018)](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6026199/fullTextXML) · [Maintaining cladding, Bygg og bevar](https://www.byggogbevar.no/pusse-opp/tre/artikler/vedlikehold-av-panel/) · [Leaves on the line, Network Rail](https://www.networkrail.co.uk/running-the-railway/looking-after-the-railway/delays-explained/leaves/) · [Beaufort scale](https://en.wikipedia.org/wiki/Beaufort_scale) (secondary) · [Fireweed](https://en.wikipedia.org/wiki/Chamaenerion_angustifolium) (secondary)

Feet and wear: [Helbing, Keltsch and Molnár 1997](https://arxiv.org/pdf/cond-mat/9805158) · [Trampling, a meta-analysis (Pescott and Stewart 2014)](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4017817/fullTextXML) · [Desire paths](https://en.wikipedia.org/wiki/Desire_path) (secondary)
