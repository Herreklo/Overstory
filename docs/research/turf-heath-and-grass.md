# Turf, heath and grass

What Jæren's pasture, coastal heath, dune marram and the turf on rock shelves are, and how shipped games build ground like it, for the Holm tip after its rock and sea. It extends `ground-cover-and-plants.md` (formats on the M4, the placer, Firewatch, BotW) and opens the decks it left shut. (secondary) marks a claim from a summary or third party; (unverified) one no source confirmed, including our readings.

## In short

- **Every one of these grounds is shaped by a cause with a clock.** Pasture by fertiliser, silage cuts and sheep holding 5 to 10 cm; heath by burning every 15 to 25 years; marram by moving sand, which it needs; rock-shelf turf by spray, thin soil, gulls and sheep. Each change is a fact with a rate, so the ground can carry the years as the houses do.
- **The forms are big and few.** Heather plants, crowberry mats, marram tussocks, thrift cushions, the bright band of plantain above the spray, the gull's green cap: each a clump or a band with an edge, which suits "big shapes, never noise".
- **The studios grouped blades and painted the far field.** Tsushima's blades grow in clumps, because per-blade randomness "just looked random", and its far grass is an artist's texture on the ground; Horizon colours grass from its ground's textures.
- **The edges are the drama, and every source is thin on them.** Dune scarps notch and fall; paths cut wounds that blow out. No field source describes the turf lip over rock; no deck shows grass meeting rock well ("an awkward edge"), nor trails, grazing or seasons.
- **On the M4 the format question is open.** Unity 6 exposes no mesh shaders; alpha-to-coverage against hidden-surface removal is unpublished. Blades by compute and indirect draws, or clumps as instanced meshes, are the two routes.

## 1. The ground

### Jæren's green

- From the 1860s farmers were told to replace natural meadow with clover, timothy and ryegrass: "a green, productive landscape dominated by grass species", its variety left at field edges machines cannot reach (Jærmuseet, Grødaland).
- Silage is cut three times a year, four after an early spring, two in a wet one (Statsforvalteren Rogaland, secondary). Sheep graze best at 5 to 10 cm: in at about 10, moved on at about 5, three weeks' rest (Geno, *Innmarksbeite*).
- Too rich or too hard grazed, a sward takes thistles, docks and nettles; trampled ground erodes (NatureScot 2020; *Beiting i kystlynghei*). Sheep tracks run along slopes of 15° to 35°, under a metre wide, one to two metres apart (GSA 2009, secondary).
- Stones cleared from the fields are the walls and cairns (Jærmuseet). In reference 56 the infield is one even, saturated green with mower tracks, bare earth where sheep stand at the fence, the walls' grey on top (our reading).

### Coastal heath

- After a burn: herbs and many small heather plants (0 to 6 years), heather leading again (6 to 15), mature and woody, time to burn (15 to 25), gaps and much moss after 25. Burning runs 15 October to 15 April in a mosaic of small burns; thin soil on rock can burn away (Statsforvalteren, *Lyngsviing*).
- About a hectare a ewe. Grazed too hard, heather goes flat-topped and thistles come; too little, tall grass falls over and rowan, birch and aspen arrive (*Beiting i kystlynghei*).
- Heather stands 10 to 50 cm, crowberry 5 to 30 cm and stays dark green, cross-leaved heath 15 to 40 cm on wet ground (SNL). Heather flowers purple from late July, goes bronze in winter (secondary), and dies back after droughts (UiB).
- Exposed maritime heath is usually under 10 cm, wind-shaped over every bump, open on rock; grazed, a mat 2 to 3 cm high (Rodwell, H7); up to 40% bare (NatureScot 2020). About 90% of Norway's heath is lost or overgrowing; juniper and birch close it in 20 to 40 years (Miljødirektoratet 2019).

### Marram and the dunes

- Sand buried farms at Orre, Reve and Vik from the late 1600s; marram planted from about 1870 held it. Dunes stand 6 to 8 m at Bore, 15 m at Revesanden (Tørum and Gudmestad 2014; Coastal Wiki).
- Marram: tussocks a metre high, 150 to 200 shoots a square metre, grey-green rolled leaves, gold spikes in July and August; it outgrows a metre of burial a year and fails once the sand stops (Rodwell, SD6; NRW).
- On Jærstrendene, protected since 1977, paths from car parks cut "wounds" and hollows blow out where tracks cross; a boardwalk lets a dune heal (Statsforvalteren 2019).
- Waves cut a notch at the foot; the overhang falls when its weight wins; plants return in 2 to 8 years (Coastal Wiki). References 54 and 55 show a turf lip over each scarp and tussocks bleached gold in low sun (our reading).

### Turf on rock and on islets

- On sprayed rock plants hold only in cracks (NIBIO). Inland come red fescue and thrift turf with sea plantain, then a "brighter green band" of plantain sward, then heath; cliff-top soil is very shallow (NatureScot 2020).
- Gulls' droppings make a lush, scruffy green on ledges and skerry tops (NIBIO; Rodwell, MC7). Kvitsøy put 351 sheep on 47 islets in 2020 (secondary; Kvitsøy 2020). Grazed cliff tops erode to bare soil; ungrazed ones go rank (NatureScot, Mull of Galloway).
- The turf edge over rock (a lip, an undercut, a rolled root mat, a sheep's scrape): no source found (unverified).

### What changes it, and how fast

| Cause | What it does | Clock |
| --- | --- | --- |
| Burning | Heath back to pioneer | Every 15 to 25 years |
| Grazing stops | Grass tall, then juniper and birch | 20 to 40 years to close |
| Grazed too hard | Flat heather, bare soil, thistles | Years |
| Feet | Wounds, blowouts where paths cross | A season; plants back in 2 to 8 years |
| Storm | Notch and scarp | One night |
| Gulls | Green cap | Years |
| Fertiliser, reseeding | Even green ley | From the 1860s; today |

## 2. How games build it

Primary, all PS4: Tsushima (Wohllaib 2021), Horizon Zero Dawn (van Muijden 2017; Sanders 2018), Uncharted 4 (Brinck and Maximov 2016).

- **Blades against cards.** Tsushima tried cards: wind moved the whole card and overdraw was too high. Each blade is a Bézier curve built in the vertex shader from its index, 15 vertices near and 7 far; normals tilt outward for a rounded look. Horizon's blade prototype "took up the entire frame"; it shipped alpha-tested clumps of 32 triangles about 1.5 m across; alpha-tested assets took about 21% of its frame.
- **Clumps.** Tsushima groups blades in a Voronoi of jittered points; the clump sets height and facing. Without it fields looked "like grass you'd want to golf on". Colour between clumps stays "very small to maintain our painted look"; flowers grow in swaths "as if painted there by giant brush stroke".
- **Placement.** Tsushima: maps per world tile, about 39 cm a texel, of height, material, grass type and grass height; a compute pass jitters a grid, culls and feeds indirect draws, about a million blades considered and 83,000 drawn in about 2.5 ms; type borders dither. Horizon: density maps from node graphs over painted world maps and about 100 ecotopes; points by ordered dithering of a disk-packed pattern scaled to each footprint (sedge 1 m, bush 3 m, tree 6 m); about 250 µs a frame. Both are deterministic and stable when the ground is edited.
- **The far field as colour.** Tsushima called it "one of the biggest struggles" and shipped "an artist authored texture" on the terrain. Horizon sinks grass into the ground with distance; grass, rocks and ground read one colour texture, so they match. BotW treats the far field as 2D (CEDEC 2024, secondary). A Short Hike keeps shading flat, otherwise "noisy" (GDC 2020); The Witness: "Minimize the amount of noise" (Antonio 2014).
- **Wind.** One field drives everything: Tsushima's scrolled Perlin noise plus a sine bob phased per blade; Horizon's springs in 3D textures, with ambient motion 80% of its grass's movement; Uncharted 4's one gust texture; Sea of Thieves' one synced vector (Ang 2018).
- **Meeting rock and paths.** Tsushima grows grass only on terrain; meshes blended into it gave "an awkward edge or worse grass poking out". Horizon multiplies roads, water and objects, as distance fields, out of its densities. A Short Hike paints paths with sharp edges. Uncharted 4's moss answers "hard plastic" with sheen, a tinted wrap, a fuzz layer and AO that fades at glancing angles.
- **Trampling and grazing.** Tsushima pushes blades from a displacement buffer; Horizon had nothing; Uncharted 4's particles write push into a render target that can persist. No deck shows trails, cut or grazed grass, or seasons.
- **Shadows.** Tsushima raises the terrain to grass height for the shadow map and skips SSAO ("a splotchy and glittery mass"); Horizon's far shadow mesh is neither alpha-tested nor animated.

## 3. On our machine

- The M4 (Apple GPU family 9) has mesh shaders in hardware, but **Unity 6 does not expose them** (WWDC 2022; tech talk 111375; roadmap, secondary). MSAA stops at 4× (Metal feature tables).
- Dense blades fill the tiled vertex buffer and split the pass ("partial render"); every varying and every shadow cascade adds to it (WWDC 2020; Rosenzweig, secondary). Apple says nothing on alpha-to-coverage against hidden-surface removal; a meadow of such cards may make most pixels MSAA edges (our reading).
- The GPU Resident Drawer needs a GameObject per instance, DOTS-instanced shaders and Forward+, and culls by bounding sphere: fit for clumps, not blades. `RenderPrimitivesIndexedIndirect` leaves per-view culling and every URP pass to us. Terrain details lose colour noise when instanced (Unity 6 manuals).

## 4. Approaches worth prototyping

Each is judged by one still beside the tip's references, in grey light first.

- **A. The ground carries the grass; strokes only near.** The ground's shader paints the sward's value shapes from fields (sward height, grazing, wetness, soil depth); opaque blade clumps by compute and indirect draws only within a few metres. Test: grazed pasture to a wall, ground alone beside ground with clumps, at the street stop and at eye level.
- **B. Plants as made clumps.** Heather plants, crowberry mats, marram tussocks and thrift cushions as opaque mesh families in several versions, placed from the same fields by footprint (Horizon's dithering), drawn through the GPU Resident Drawer, ground between. Test: one 12 m still of heath over rock and a dune crest, clumps beside alpha cards.
- **C. Turf as a mat with an edge.** A turf skin with thickness wherever the soil-depth field is, ending over rock in a modelled lip, undercut or torn root mat: a part, not a blend, against Tsushima's "awkward edge". Test: one eye-level still from the water on the rock lane's low frame, modelled edge beside shader blend.

## Gaps

- The turf edge over rock, sheep scrapes, rush patches, terracette risers, burn patch sizes, heath heights by phase.
- Draw distances and blade sizes in metres (no deck gives them); Samurai Landscapes (not reachable); Nintendo's, Rare's and Awaceb's grass.
- Measured grass on M-series GPUs; Apple's alpha-to-coverage behaviour.

## Sources

Ground: Jærmuseet (Grødaland; samlingar p550) · Statsforvalteren Rogaland: *Lyngsviing*, *Beiting i kystlynghei*, Jærstrendene 2019, silage · Miljødirektoratet 2019, *Faggrunnlag kystlynghei* · Geno, *Innmarksbeite* · Tørum and Gudmestad 2014 · Rodwell, NVC H7, SD6, MC7 · NatureScot conservation advice 2020 (Fair Isle, Mull of Galloway, Cape Wrath) · NRW marram note · NIBIO, strandberg · Artsdatabanken T8 · Kvitsøy SMIL 2020–28 · SNL · UiB · Coastal Wiki · GSA 2009. Craft: Wohllaib, GDC 2021 (youtube Ibe1JBF5i5Y) · van Muijden, GDC 2017 (guerrilla-games.com) · Sanders, GDC 2018 (youtube wavnKZNSYqU) · Brinck and Maximov, SIGGRAPH 2016 · Robinson-Yu, GDC 2020 (youtube ZW8gWgpptI8) · Antonio, GDC 2014 · Ang, SIGGRAPH 2018 · secondary: gamebusiness.jp (CEDEC 2024). Machine: Metal feature set tables; WWDC 2020 10602, 10603; WWDC 2022 10162; tech talk 111375; Rosenzweig (Asahi); Unity 6 manuals.
