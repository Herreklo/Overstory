# Land, rock and water

How the best studios, researchers and painters build terrain, natural stone, the coast and the sea, and what that means for a harbour town on bare rock built in Unity 6 URP from Blender generators. Part of the craft studies beside `materials-at-scale.md`, `history-in-things.md`, `performance-at-scale.md`, `kits-and-generation.md`, `lighting-and-colour.md` and `animation-and-motion.md`. The subject side (what grows where, the town's stone) is in `docs/nature.md`, `docs/research/nature.md`, `docs/research/vegetation.md`, `docs/stone.md` and `docs/research/stone.md`. Claims taken from a summary or a write-up are marked (secondary); claims we could not confirm are marked (unverified). Arithmetic of our own is marked (ours). Many talks sit behind GDC Vault's login; where only the abstract opened, we say so.

## The bottom line

1. **A height field is the soft ground, and nothing else.** It cannot hold an overhang, and it cannot hold a crisp edge unless its vertices lie on the edge. Every shipped game that looks good on steep ground lays meshes over the height field there. Far Cry 5 generates cliff meshes from slope. Firewatch layered rock meshes over its stretched cliffs by hand. Ghost of Tsushima's terrain team authored "custom cliffs and rock arrangements" (secondary). Our clay shows the same limit: Watch Knoll's ledges, cut into a 1.5 m grid, read as saw-teeth from the city camera (`reviews/lt1/heart/clay/heart-clay-8-watch-knoll.png`).
2. **Our land is shaped by ice and rock structure, not by rivers.** Erosion simulators (Houdini, Gaea, World Machine, the papers) carve dendritic gullies and talus fans. The west coast is scoured bedrock: smooth sloping slabs (*svaberg*), knolls with a gentle abraded side and a plucked, stepped side (*rundsva*), shapes set by joint spacing and foliation. Stavanger's own rock is phyllite and mica schist in bands of metres to tens of metres, laminated, from graphite-dark to grey-green, rusty in places (NGU 2024). Thermal erosion for talus and flow for where water goes are useful; carving is not.
3. **The land has a history like everything else.** Quays are fill, lanes are cuts, yards are terraces, a rock face beside a lane was blasted in a year that its drill holes still show. CityEngine keeps the original height map and stores every alignment as a separate elevation delta with its cut and fill. That is the shape our data should take: natural ground from the pack, then dated made-ground acts on top, each one with a cause, an edge treatment and a year.
4. **Fields over the land do the work that painted masks do elsewhere.** Horizon Zero Dawn keeps "a collection of 2D maps", all generated and all paintable, at about 4 MB a square kilometre. Among them: terrain height at 0.5 m, rock colour and lichen density at 1 m, erosion flow, wear and deposition, cavity and water flow. Frostbite picks terrain materials in the shader from height and slope; Ghost Recon Wildlands from slope, height, flow, deposition and curvature. Ours come from facts (soil depth, wetness, feet, exposure, years bare), so one ground shader can choose few materials with crisp edges.
5. **Mesh terrain from our own generator beats Unity Terrain for this town.** Unity Terrain projects textures top-down and stretches them on cliffs. Firewatch tried box projection and found it drew the terrain twice. Its lead artist said they underestimated optimising the terrain "until we were past the point of doing something custom about it". Our ground must stop at walls, quays and rock faces along breaklines, carry our baked fields and use the town's one shade function. A chunked mesh in rings of 0.5, 2, 8 and 64 m costs about 370,000 triangles for land from the street to the horizon (ours).
6. **The harbour is ripples, not swell.** In a fresh 10 m/s breeze, fetch-limited wave formulas give the Basin (fetch about 550 m) waves of about 12 cm and 1.5 m wavelength. The Roads (3 km) get about 28 cm and 4.6 m (ours, from the Coastal Engineering Manual's formulas). A sum of eight to twelve Gerstner waves sized per water body from wind and fetch, plus two detail normal maps and rain rings, is enough. FFT ocean is for the open fjord, if ever.
7. **Water is two different things at our two kinds of view.** Near the surface its reflection dominates; from 35 m up and near-isometric, Fresnel leaves about 2 percent reflection, and the water reads by its own body colour and its depth. So bake depth (bathymetry) from the land into the water mesh and draw the colour from it; that works with opaque water and with URP's new screen-space reflections. Lamps at night stretch into vertical columns on rippled water (Minnaert); Hasui printed them as amber streaks in dark blue. Our lamps are facts (`TownLights`), so their columns can be drawn from the lights list rather than hoped for from a blurred reflection.
8. **The shore is a set of bands set by tide and exposure.** Stavanger's spring range is about 46 cm (secondary), so quay bands are narrow; spray widens the lichen zone on exposed rock (MarLIN). Above high water: black *Verrucaria*, then orange and yellow, then grey lichens; below it, in order down the shore, channelled wrack, spiral wrack, bladder wrack, knotted wrack on sheltered shores, serrated wrack, then kelp (SNL). Shingle beaches are steep (about 1:5), fine sand gentle (to about 1:100; secondary).
9. **Parts date the land, surfaces age it** (`history-in-things.md`). A hand-drilled cut (hand drilling held in Norway until the Second World War, geo365) differs from a machine-drilled or presplit one, whose half-barrel holes are 5 to 10 cm across (secondary). A quay's construction dates it. Lichen, turf over a bank and weed in a fill tell how long ago.

## 1. Terrain

### What a height field can and cannot do

Galin and colleagues' review of terrain modelling (Eurographics 2019) defines the usual terrain as an elevation function over the plane, and says plainly that this "restricts modeling to terrains without overhangs, arches, or caves". A grid height field's precision is its cell size; between samples the surface is interpolated. Eight-bit heights "introduce visible step patterns". Heightfields are "the most common data representation for digital terrains in the industry"; in film they are "completed with representations that allow true 3D features".

The review's second representation matters more to us: **layered fields**, a bedrock elevation with the thickness of each material on top (rock, sand, water), as Musgrave proposed in 1989 and erosion work has used since. A layered land answers questions a single height cannot: how deep the soil is over the rock (so where heath, moss or bare rock grows), where fill lies over the old shore, what a cut exposes.

A crisp edge is the other limit. On a regular grid, an edge that is not aligned to the grid becomes a staircase, however fine the grid. Surveyors solve this with **breaklines**: a triangulated surface (a TIN) whose edges are forced along known lines, hard where the slope breaks sharply (a wall's foot, a kerb, a cliff's top) and soft where only the height is known (Esri's TIN documentation). Our clay solves the land on a 4 m Laplace grid and draws it on 1.5, 6 and 60 m grids; the knoll's ledges come from a floor function that steps across the grid diagonally, and that is the saw-tooth in the clay frames.

### Generation and erosion, and how little of it fits us

**Thermal erosion** moves material downhill wherever the slope passes a talus angle, typically 30 to 45 degrees for earth forms (Galin). It is simple, intuitive, makes scree cones at cliff feet, and has one known fault: "even when the talus angle is set with random perturbations, slopes look unnaturally similar". Geologists prefer a diffusion term for soil-covered hillslopes. Thermal erosion on a height field cannot make overhangs; Peytavie's Arches (2009) does it in a hybrid volumetric model, limited to about a kilometre cube.

**Hydraulic erosion** comes in grid (Eulerian) and particle (Lagrangian) forms. Mei, Decaudin and Hu's virtual pipes (2007) made it interactive on the GPU; Šťava and colleagues (2008) added layers and passed 1024 squared. The review names two fundamental problems: scale (simulating at a small scale and scaling up "is intrinsically flawed") and control (users set initial conditions and wait). It is mostly used "as a beautification process" on a procedural base.

**Stream power** (Cordonnier and colleagues, 2016) erodes by drainage area and slope against tectonic uplift and builds whole mountain ranges, solved implicitly in linear time. **Glacial erosion** was listed in 2019 among phenomena "seldom or never addressed in computer graphics"; Cordonnier, Jouvet and colleagues (SIGGRAPH 2023) then simulated glaciers and their erosion over glacial cycles, producing U-shaped and hanging valleys and fjords.

The tools wrap these. Houdini's HeightField Erode writes height, sediment, debris and flow layers, with hydraulic terms (flow force, bank angle, rainfall, erosion and deposition rates) and thermal ones (cut angle, repose angle), and clamps its feature size to at least three voxels. Unity's Terrain Tools package has hydraulic, thermal and wind brushes; its thermal erosion "doesn't increase angles, only decreases them", and detailed features want a heightmap of 1025 or more. Gaea's free Community edition is for evaluation and non-commercial use and exports up to 1024 squared; its EULA restricts use in products whose main purpose is terrain generation. Ghost Recon Wildlands used World Machine for its terrain and derived maps (secondary); Firewatch used World Machine for "a few landscape props that are not traversable".

None of this is our land's main story. The west coast is glacially scoured rock:

- A *svaberg* is "a bare, sloping rock, especially by the sea", flat or tilted, usually smoothed by ice (SNL).
- A *rundsva* (roche moutonnée) has a gentle stoss side facing the ice, abraded, and a cut-off lee side where the ice tore blocks away (SNL).
- Joints set the scale. In south-west Finland, the fewer and smaller the joints, the larger the roches moutonnées, and vertical joints along the ice flow set their width (Rastas and Seppälä, secondary). At Ullapool, widely jointed sandstone gave smooth whalebacks and closely jointed quartzite gave plucked lee faces (secondary). Plucking follows the joint and fracture systems.
- The strandflat, a gentle erosion surface from 60 to 70 m above to 30 to 40 m below today's sea, runs along the coast from Ryfylke northward and breaks into "countless" islands, holms, skerries and reefs where it lies near sea level (SNL). That is the Roads: the Teeth, the Pip, Gull Island.
- Stavanger's bedrock is phyllite and mica schist (the Ryfylke schists), "strongly deformed", alternating "on the metre to centimetre scale" (NGU report 2024/034). It comes in dark graphite-rich, grey-green chlorite-rich and lighter quartz-rich variants that change over metres to tens of metres. Graphite-rich areas can look rusty, and NGU compared rusty surfaces with fresh ones in the same rock. A core from the Hundvåg tunnel was drilled east to west, "perpendicular to the strike", so the foliation there strikes about north to south; the dip is not stated. The rock is laminated, with visible layers of colour and grain, and crush zones along faults.

So the land's shapes come from three vectors and one material:

- the ice's direction: which side is smooth, which plucked;
- the foliation's strike and dip: which way ledges run and lean;
- the joint sets: block size and the facets of faces;
- the rock kind: phyllite should pluck into thin stepped ledges and flakes, gneiss and granite into broad whalebacks (ours, from the joint-spacing studies).

Rain then only washes, stains and gathers in hollows; it does not carve at the scale we see. The ice direction for this coast is not settled in what we found. An NGU bulletin reports southward striae on Jæren through most of the Weichselian, while the Norwegian Channel's ice stream ran north offshore (secondary, conflicting).

### How shipped games build terrain

| Game | How the land is made | What we take |
| --- | --- | --- |
| Horizon Zero Dawn (Guerrilla, GDC 2017 slides) | World data as 2D maps "streamed in sections, all generated, all paintable, ~4MB/km²": Height_Terrain, Height_Objects and Height_Water at 0.5 m; Variance_RockColor and Variance_Lichen_Density at 1 m; Erosion_Wear, Flow and Deposition, Terrain_Cavity, Water_Flow at 0.5 m; Topo_Roads, Topo_Water, Topo_Objects. Placement of all nature on the GPU, deterministic and locally stable, about 250 µs | Fields at 0.5 to 1 m, generated from data; separate heights for terrain, objects and water |
| Ghost of Tsushima (Sucker Punch) | A rule language compiled to GPU bytecode for texture and placement rules (GDC 2021 abstract; the talk would not open); the terrain team sculpted large-scale terrain and authored "custom cliffs and rock arrangements" (secondary); ground and leaves photo-scanned on the island (secondary) | Rules for texture and placement from the same data; cliffs as authored meshes |
| Far Cry 5 (Ubisoft, notes on the GDC 2018 talk, secondary) | Cliffs generated from slope: below a threshold the surface is deleted, the rest remeshed, sliced into strata of random thickness at painted angles, extruded and displaced; cliff textures "transferred to the terrain beneath"; rocks scattered on the erosion area, trees on raycast ledges; a flow simulation extends the cliff mask as erosion; a strata tint stays on the terrain when the cliff mesh unloads; 64 m sectors | Cliffs and ledges as meshes from rules; the ground beneath takes the cliff's colour; a far tint that survives unloading |
| Ghost Recon Wildlands (Ubisoft, 80.lv interview) | Procedural terrain materials (TPS and TPM) placed by slope, height, flow, density, deposition and curvature, four foreground textures each; puddles flatten the normal and override albedo; rocks sculpted, scattered by Houdini from curvature, slope and cliff detection, kept out of camps, villages, roads and paths | Material choice from fields; rocks avoid where people go |
| The Witcher 3 (CD Projekt Red, GDC 2014 abstract) | Geometry clipmaps (secondary); moved away from "conventional terrain material layers and linear blends"; a control map with a base and an overlay material per point, as copied by Terrain3D (secondary); vegetation generated offline and at run time | Two materials and a blend per point, not N weights |
| Battlefield (Frostbite, SIGGRAPH 2007 notes) | Procedural shader splatting: height and slope computed in the shader, masks from ramps (a mountain material between two slopes), detail added by an overlay blend with tiled masks, sparse painted masks only for what rules cannot make (fields), destruction masks | Rules first, painted exceptions rare and sparse |
| Firewatch (Campo Santo, GDC 2016 slides, blog) | Unity Terrain; top-down texture projection stretched on cliffs; box projection drew the terrain twice; "layering rock meshes on top of areas with a lot of stretching, but very labor intensive"; terrain shadows off, proxy casters underneath; ZBrush rocks; greybox, then paintovers, three to six passes | Rock meshes over every steep face, by rule rather than by hand; proxy shadow casters |
| Breath of the Wild (Nintendo, CEDEC 2017, secondary) | Terrain shaped as "triangles" that hide and reveal what lies beyond, of many sizes | The land as composition: knolls and spurs that hide and reveal (Cullen's serial vision, already in the plan) |
| Sable (Shedworks, GDC 2022, secondary) | Dunes thought of as a seascape with "islands of content", about 10 by 10 km; depth read from light, fog and lines that fade with distance | Air and fog as the reading tool; open ground as orientation |
| Red Dead Redemption 2 | No terrain talk found. A frame study shows footprints drawn into a 2048 squared mud map driving parallax on the terrain (secondary, in `performance-at-scale.md`) | History of use kept in a texture over the ground |
| Tiny Glade (Pounce Light, 80.lv interview) | Many small GPU generators; buildings first stuck to the terrain, then "a whole system for elevating buildings", which raised support and overlap | Foundations are generated from the ground's need |
| Dishonored 2 (Arkane, Bethesda article) | Karnaca's backstory went back two centuries, including "the very shape of the landmass itself"; silver quarries "shifted the landscape and shaped the districts" | The land itself has a dated history |

### Texturing the ground at scale

The studios agree on three things. Choose the material per point from data (height, slope, flow, curvature, deposition), not from a hand-painted weight per layer. Add detail by a cheap combination of a smooth mask with a tiled grey detail texture (Frostbite's overlay blend keeps the base mask where it is 0 or 1). Keep painted exceptions sparse; Frostbite stored painted masks in a quad-tree of 32 by 32 tiles so empty ground costs nothing.

Steep faces are where height-field texturing fails. Unity Terrain projects from the top; Firewatch's answer was rock meshes. Triplanar projection works but costs three samples per layer; Far Cry 5 instead lets cliffs be meshes and transfers their texture to the ground under them so the seam does not show.

Unity's URP terrain draws four layers per pass, with "no limit on the number of passes"; each extra pass adds time, so the manual advises four layers per tile. Height-based blending in URP renders "only the Terrain Layer with the greatest height value" for a pixel, with a set transition width. Per-pixel normals from the heightmap need instanced drawing.

Repetition is solved the way `materials-at-scale.md` recommends for every continuous surface: hex-tiling (Mikkelsen, JCGT 2022, from Unity), with a seeded offset per piece where the ground is cut into chunks.

For our style the lesson is narrower. Few ground materials (turf, heath mat, moss, bare soil and mud, gravel, sand, shingle, rubble fill), chosen by fields; a crisp edge where two communities meet, thresholded against noise, never a smeared blend; painted at our scale with value in the pigment. `docs/visual-direction.md` already asks for "ground cover in clusters with edges, never noise".

### Unity Terrain against mesh terrain

| | Unity Terrain | Our chunked mesh from Blender |
| --- | --- | --- |
| Shape | regular grid, 33 to 4097 samples a tile; no overhang; no breaklines | any triangulation; breaklines along walls, kerbs, quays and rock outlines; holes are just missing triangles |
| Steep faces | top-down projection stretches (Firewatch); triplanar means a custom shader | rock and wall parts cover them; the ground stops at their foot |
| Texturing | four layers a pass; splat weights; height blend | our ground shader on the town's shading (`StreetLooks.hlsl`), fields as textures per chunk |
| Our bakes | no per-vertex data; would need textures for the sky, water and history channels | the same channels as every other part, or the same history maps (`materials-at-scale.md`) |
| LOD | built-in quadtree by pixel error; instanced drawing | ours: rings per chunk; Unity's Mesh LOD or our own levels |
| Holes | texture-based, aliased edges, downscaled with resolution (manual) | exact |
| Shadows | the visual mesh casts; Firewatch turned it off for proxies | a coarse caster per chunk |
| Editing | brushes, erosion tools | none by hand; the generator rebuilds from facts |
| GPU Resident Drawer | no (the drawer covers Mesh Renderers) | yes, as Mesh Renderers |

Unity Terrain's strengths are for hand-authoring, which we do not do. Its weaknesses fall exactly where our town is: walls, quays, cuts and rock faces. The verdict agrees with `performance-at-scale.md`, which already plans the land as a chunked mesh with ledges as natural stone.

The budget is modest (ours). A uniform 0.5 m grid over the heart (930 by 810 m) would be 6 million triangles, more than a whole frame's 4 million. Rings fix it: within 64 m at 0.5 m, about 103,000 triangles; 64 to 256 m at 2 m, about 97,000; 256 m to 1 km at 8 m, about 97,000; out to 7 km at 64 m, about 75,000. That is about 370,000 before frustum culling, and in the town most near-ring ground lies under paving and houses and is cut away.

## 2. Rock and cliffs

### How studios make rock

**Sculpted.** Firewatch sculpted rocks in ZBrush and baked them to game meshes. Its lead artist, Jane Ng, distilled "rock" to "smooth surfaces interrupted by jagged edges and detailed divots" (Campo Santo blog, Firewatch art Q&A part 2, 22 October 2014). The divots and jagged edges are sculpted and baked to a normal map. The diffuse is almost flat grey with the occlusion bake multiplied in, and the edges are highlighted like drybrushed miniatures. Soft contact occlusion grounds it. Less is more: no more than about 30 minutes of sculpting per rock. A distance fog by colour ramp lowers texture noise once a rock leaves the foreground. Most of its rocks have a grey diffuse; their colour comes from the light, the fog and the grade (part 3). Age is modelled in by cause, such as smaller rocks and a dirt pile at the foot of a steep slope. Wildlands sculpted at high resolution, baked normals for the global shape, and exposed shader parameters for occlusion, curvature, tiling, edge aberration and "Z materials" for dirt, snow and moss. One cliff kit on The Rookies was sculpted so that its pieces meet inside their own deep cracks, which hides the seams (a student entry, secondary).

**Scanned.** DICE built Star Wars Battlefront on photogrammetry (GDC 2016; the talk would not open); Ghost of Tsushima scanned ground on the island (secondary). Megascans were free to all until the end of 2024 and are now mostly paid, with a free subset of about 1,500 assets (secondary). Poly Haven's scans are CC0 (unverified here). Scans carry light and photographic detail in their surface, which our rules forbid (`docs/stone.md`: value painted into the pigment, shade from the light). They are useful for study and for form, not as our surfaces.

**Generated.** Far Cry 5's cliffs come from slope and painted strata angles. Peytavie's 3D thermal erosion splits cliffs into Voronoi blocks that detach and pile up. Houdini scatters rocks by curvature and slope.

**Cut from one mass, then scattered** (28 October). Naughty Dog sculpted one formation and split it into five chunks that reassemble into the whole or serve alone, turned to show other sides (Sobotta, TLOU Part I). Gunfire's tool slices a volume into strata with planes and moves each slab rigidly instead of displacing it, then chips edges with a cutter (Skidmore, 80.lv). The Witness builds each formation from its rock type, and the blocks at a face's foot share the face's shapes (GDC 2014). Unity's rock sample computes colour and top cover in world space over the assembled formation, so its pieces read as one. Battlefront fades detail before LOD0 ends and drops it from LOD1's shader; Variational Shape Approximation coarsens a mesh into its best-fitting planes. No source covers svaberg or a drawn sea band; the usual runtime wet band is a height test broken by noise. For us: cut each outcrop from one mass along its joint sets, its talus from its own chunks; compute the history fields once on the formation, per vertex; take top cover and value per cause plane; let only the sea bands cross planes; coarsen by structure, dropping chamfers and minor cuts first.

### Rock as deliberate planes, with reasons

Another World built its world from flat polygons. Chahi has said he "lost detail" with the style but gained huge animations and cuts with no loading (secondary, interview). Firewatch's rocks are chunky planes with crisp chamfers, two or three values each (`docs/references/stone/` 21, 22). Hertervig painted Stavanger's boulders as "big planes of light and shade" with the texture only at the edges (board 17). Gurney's note on overcast light gives the rule for our default weather: soft light lightens the up-facing planes, and planes darken as they face progressively down, with no sharp line between light and shadow (secondary). In drizzle a rock reads only if its planes are big and differently tilted. We found no developer source on how Tiny Glade's rocks or Ghost of Tsushima's cliffs are shaped. Tiny Glade's general method is many small generators, each a pipeline "that supports creation, assembly, morphing, or deforming", with every rule written by hand (80.lv interview).

Our addition is that the planes have causes. A rock's faces are its joints, its foliation and the ice's work:

| Face | Cause | Shape | Value in drizzle |
| --- | --- | --- | --- |
| the top, stoss side | ice abrasion | broad, smooth, gently rounded; striae at eye level only | the lightest plane |
| a lee face | plucking along joints | stepped, angular, in blocks the joint spacing sets | middle to dark, with dark recesses |
| a ledge | foliation or a horizontal joint | a thin shelf along the strike, leaning with the dip; soil, moss and heather on it | a light strip over a dark riser |
| a joint face | a near-vertical joint set (often two, near right angles, as board 15 shows) | flat planes, edges chipped a little | by facing |
| a cut | blasting, dated | flat, with half-barrel drill traces and fresh colour | lighter and less grown than natural faces |
| a sea face | wave scour and spray | smooth below, black lichen band, orange above | darkest at the foot |

A generator follows. Start from a rough volume, the outcrop's outline and height from the land. Cut it by the pack's joint sets at their spacing and lean it by the foliation. Smooth the stoss side and step the lee side by the ice vector. Then chamfer each edge by the rock kind. That is Another World's discipline with geology's reasons. It ties every rock in town to the same three vectors, so a viewer reads one land.

### The forms this town needs

| Landform | In the plan | Rock kind (to decide) | Built as |
| --- | --- | --- | --- |
| The corner's knuckle | 14 by 18 m, 1.4 m face to the lane, cut in the 1870s | the town's own rock | one natural-stone part: a natural top and sides, a dated cut face to the lane |
| Watch Knoll | 44 m, ledges in slanting bands on the harbour and Holm Street sides, a long gentle back | phyllite | a soft height field for the back; a ledge kit laid along the strike, the Crack as a joint |
| The Bluff | a 20 m face over the Roads | phyllite or gneiss | a face kit with a talus apron, a black spray band at its foot |
| The Holm's tip, the beacon islet, skerries | bare rock islands | the same | svaberg slabs into the water, zoned by spray |
| Bedrock in yards and behind houses | "bedrock breaking through where it was too hard to cut" | the same | small outcrop parts sunk into the soil depth field |
| Boulders on the heath and in Tower Wood | erratics from the moraine | gneiss or granite, foreign to the bedrock | boulder parts half-sunk; cleared ones in walls and cairns |

Watch Knoll as drawn (`centre_land.py`, `KNOLL`) has its ledgy, rocky sides to the north (the sea) and east (Holm Street) and its long gentle back to the south-west. Read as a roche moutonnée, that means ice moving north-east, which neither the southward striae on Jæren nor the seaward flow from the mountains suggests (unverified). Read as a dip-slope knoll, the gentle back follows the foliation's dip and the steps cut across it, which phyllite makes natural and which keeps the plan as it is, if the foliation dips to the south-west. The pack should write down one ice direction and one foliation strike and dip for the town, and every knoll should obey them.

### Boulders half-sunk in turf

The heath and Tower Wood's old pasture carry erratics from the moraine; Jæren's moraine is clay, sand, gravel and stones over phyllite (`docs/research/vegetation.md`). A boulder that has lain since the ice is sunk by soil and turf built up round it, so it shows a turf lip, not a contact line. Where fields were cleared, the stones went into walls and clearance cairns, so a field's boulders are a dated fact: cleared with the field (on Jæren mostly from the 1860s), left where the heath stayed. The common practice in games of burying a third of a rock is a rule of thumb (unverified); ours is the soil depth field, which says how far the turf has climbed.

### How rock meets the ground

Four things make the meeting read.

- **The ground takes the rock's colour.** Far Cry 5 transfers cliff textures to the terrain beneath. Unreal's Runtime Virtual Texturing lets meshes blend into the landscape through the same cached texture. Unity URP has neither virtual texturing nor RVT (`performance-at-scale.md`). We can bake a top-down ground map per chunk (the ground's colour and fields), as the sky map is baked, and let rock, wall and plinth shaders read it at their foot.
- **The rock changes the ground.** Far Cry 5's assets raise and texture the terrain round them ("plants change the ground"). A rock throws a rain shadow on its lee, a drip line under an overhang, a damp foot, shelter for ferns and moss. Each rock writes into the water, sky and wind fields, and nature reads them.
- **Debris lies where it falls.** Scree and blocks at a cliff's foot at the talus angle (30 to 45 degrees; Galin), sized by the joint spacing. Thermal erosion on the soil layer makes the apron; the blocks are parts.
- **Turf has an edge.** On thin soil over bare rock, heather, crowberry and moss form mats whose edge is a lip over the rock (our observation, unverified). It is exactly the "clusters with edges, never noise" the direction asks for, and it comes from one field: soil depth.

### Lichen, streaks and moss on rock

The growth and water systems already have the rules; rock is a new surface for them.

- Lichen on lit, dry, quiet faces, sized by years bare: map lichen about 0.75 mm a year in maritime west Norway (`docs/research/stone.md`); *Xanthoria* where birds perch; woolly fringe-moss (*Racomitrium*) in grey mats on exposed rock (`docs/research/vegetation.md`). A cut face is bare from its cut year; a natural face has been bare since the ice, so its lichen is at its full cover.
- Moss on up-facing ledges and in damp feet and joints. Board 11 shows moss on tops and upward faces while vertical faces stay grey.
- Streaks where water runs: on Alpine rock, black stripes ("ink lines", *Tintenstrich* communities) form mostly along runoff paths, made by lichens with cyanobacteria or green algae (Eawag, secondary). `water.py` already traces where water runs and drips; on rock it is the same trace on a different surface.
- Rust from the phyllite (NGU notes rusty surfaces; the county governor warns it can be rich in sulphides, secondary), as a carried stain below rusty bands (`history-in-things.md`, carried stains).
- By the sea, the spray zone's bands (Coast, below).

### Parts date a cut

`history-in-things.md` found that parts date a place and surfaces age it. For rock the parts are the marks of making. In Norway the first gunpowder blast is said to date from 1655. Better steel drills and dynamite came in from the 1860s, as railway building gathered pace. Hand drilling "held right up to the Second World War", because wages were low and early machines heavy. On the Gravhals tunnel (1900 to 1906), water-driven and then compressed-air drills took over from hand drilling (geo365). Presplitting leaves half-barrel traces of holes 5 to 10 cm across along the face, hard to remove without taking the whole outer layer (FHWA, secondary). So a cut of the 1870s shows short, irregular hand-drilled holes, and one of the 1960s longer machine holes. One made after presplitting arrived shows a regular comb of half-barrels (date for Norway unverified). Each era's cut is a small atlas of marks placed on the cut face by the generator.

## 3. Water

### The sea and the harbour in real time

**FFT.** Tessendorf's notes (2001, rev. 2004) build an ocean from Gaussian random amplitudes with a spatial spectrum, animated by the deep-water dispersion relation, summed by FFT. The Phillips spectrum puts the largest waves at L = V²/g for a wind of speed V, and suppresses waves across the wind. Horizontal displacement makes waves choppy; where the Jacobian of that displacement turns negative the surface folds, which is where crests break and foam forms.

**Gerstner sums.** Finch's GPU Gems chapter sums a few Gerstner waves for geometry and about 15 small waves into a tiling normal map. Its practical rules:

- draw wavelengths between half and double a median, and keep amplitude over wavelength constant across waves;
- take directions within an angle of the wind, and derive speed from the dispersion relation;
- keep the steepness sum at or below 1, or crests loop;
- filter out waves too short for the mesh's edge length;
- scale amplitude down by depth near shore, so waves die on a shallow beach.

**Sea of Thieves** (Rare, SIGGRAPH 2018 talk) runs Tessendorf's FFT, then stylises it. A deep colour blends with a "sub-surface" colour by view angle, sun direction and a wave-peak mask from the chop. Foam forms at peaks and, by depth comparison, round objects in a camera-centred window; it is blurred with feedback to disperse, then blended with authored textures. "Calm water will only show foam generation around intersecting objects." An area specular gives a big low sun. Shallow incidental water runs a Mei-style surface simulation.

**In Unity.** HDRP's water system splits waves into three bands, swell (from fetch), agitation (wind chaos) and ripples, and uses only ripples for pools and ripples plus agitation for rivers (secondary, Unity's blog). It is HDRP only. Crest's free repository targets the built-in renderer only; its URP version is sold on the Asset Store. Unity's Boat Attack demo (URP, 2019.3) has Gerstner water, planar reflections through SRP callbacks, caustics and a Jobs buoyancy system. With no money for assets, we write our own, and the harbour's needs are small.

### What our water bodies need

Waves are set by wind and fetch. From the fetch-limited formulas in the Coastal Engineering Manual (via planetcalc, secondary; the arithmetic is ours):

| Water | Fetch | Wind 5 m/s | Wind 10 m/s | Wind 15 m/s |
| --- | --- | --- | --- | --- |
| The Basin, along its length | 550 m | 6 cm, 0.8 s, 0.9 m long | 12 cm, 1.0 s, 1.5 m | 19 cm, 1.1 s, 2.0 m |
| The Basin, across | 100 to 160 m | under 5 cm | under 9 cm | under 14 cm |
| The Roads | 3 km | 13 cm, 1.3 s, 2.8 m | 28 cm, 1.7 s, 4.6 m | 44 cm, 2.0 s, 6.2 m |
| The fjord beyond | 10 km | 24 cm, 2.0 s, 6.2 m | 50 cm, 2.6 s, 10 m | 80 cm, 3.0 s, 14 m |

Each figure is the significant height, the peak period and the peak wavelength. The Basin never has swell; its surface is ripples and short chop, about a hand's height in a fresh breeze. The wind's direction against each body's shape gives its fetch. A wind across the Basin's narrow width leaves it nearly calm; a north wind runs its whole length and roughens the Roads outside the breakwater. That makes the water's state a derived fact of the weather and the land, as the visual direction asks.

So the Basin needs no displaced geometry at all beyond the near ring, where a few centimetres of chop can show against a quay; its look is in normals, reflection and colour. The Roads need modest Gerstner geometry near the camera. Boats need heights at three or four points each, which an analytic Gerstner sum gives on the CPU at once, as Boat Attack does; FFT would need a readback.

### Reflections and what they cost in URP

Water reflects about 2 percent of light looking straight down and nearly all of it at grazing angles (Fresnel; Tessendorf's optics section). From eye level and the street stop the harbour is mostly reflection; from 35 m up and near-isometric it is mostly the water's own body: its colour, depth and what lies under it. Both views are main views (`docs/visual-direction.md`), so the water must be designed for both.

- **Screen-space reflections.** Unity's URP SSR "can only use information that is visible on screen"; rays that leave the screen or hit hidden surfaces fall back to reflection probes or the sky. Its thickness setting trades holes against stretching; users report low-resolution artifacts on water at half and quarter resolution; it ships in 6.7 and is already a renderer feature in our 6.6 project (Unity forum, from the developers). Our wet streets already pay for it.
- **Planar reflections.** A second render of the scene, mirrored. GTA V renders its water reflection at 240 by 120 and lets the bumped normals hide the blur (Courrèges's frame study, secondary). Boat Attack renders it through SRP callbacks. For rippled harbour water a small planar reflection of the big masses (houses, quays, boats, hills, lamps), without small props or shadows, would be enough. Its cost must be measured before it is chosen.
- **Probes.** A sky-only probe already captures the hour's sky (`StreetStage.cs`); it is the fallback for everything.

Night is where reflection matters most. On rippled water a lamp's reflection stretches into a vertical column, because only facets of the right tilt send its light to the eye; the column's length grows with the waves (Minnaert; a University of Colorado demonstration, secondary). Stochastic SSR (Frostbite, SIGGRAPH 2015) lists "specular elongation" among its goals, because isotropic blurs lose it. Hasui printed it, again and again. In LACMA's catalogue descriptions, "glowing lanterns reflect on dark blue water" in his Kanazawa canal (1920), and "teal-toned water reflects a lit window" at Matsue (1924). Shirosaki (1924) is a rainy night canal in "deep navy and black with amber accents". Atami (1947) is nearly our town: a coastal village at dusk, warm windows "beneath a steep, rocky hillside", light reflecting across dark water. Grimshaw painted the same columns in the Clyde (board 20).

Our lamps and lit windows are facts with positions (`TownLights`, `lights.json`), and the water's slope spread is known from the wind. A shader term can draw each strong light's column directly: where the light's mirror point falls on the water, stretched by the slope spread, broken by the ripple normals, coloured by the lamp's era. It costs a loop over the few nearest lights, needs no extra pass, and gives Hasui's columns whether or not SSR resolves them.

### Depth, colour and the shore

**Depth colour.** GTA V adds blue water opacity "stronger with depth" to a refraction map (secondary). A refraction pass needs transparent water and an opaque copy; our water is opaque today (`Street.shader`, `_OS_WATER`), which keeps SSR simple. The land is generated, so the water's depth at every point is known. Bake depth and a seabed colour (rock, sand, kelp, mud) into the water mesh, and let the shader mix the seabed into the body colour by an exponential of depth. The Basin's dredged quays drop away to several metres, so it reads dark; a cove's shelving rock and the beach read through.

**Foam and the shoreline.** Two methods compete. A depth-buffer threshold (Parkitect's way) is cheap but cannot animate waves toward the shore and shows only on the camera-facing side. A distance field from a top-down outline of everything touching the water can (Croakwood, from the developer). Ours is easier: the coast is a polygon in `centre_land.py`, so the shore's distance field is baked once, and only boats need a live term. Sea of Thieves' calm-water rule fits the Basin: foam only where things meet the water, and only a little. In the Roads in wind, foam belongs on the windward sides of the skerries and the breakwater, by exposure.

**Wakes.** The Penny Ferry crosses every twenty minutes. A ship's wake spreads in a wedge of about 19.5 degrees each side (Kelvin's result, standard physics), and lingers as a slow set of crossing waves. It is a scheduled fact on the water, drawn as a decal of normals and foam that fades.

### Stylised water and the target

Sea of Thieves stylises FFT water by its colour model and foam. Sable treats its dune sea as water and lets fog and fading lines carry depth. We found no primary source on the water of Firewatch or Breath of the Wild. Hasui is the lead (`docs/visual-direction.md`). In the prints, as we read them, water is a few flat graded plates of colour carrying the sky's hue, darker near and at the foot of things. Reflections of lights are broken vertical strokes, and rain is fine lines over it. A Sotheby's note on a Kinosaki rain scene points to the "softening and blurring of reflections" by the rain (secondary). That is a value plan more than a shader. At the street stop and above, the water should resolve to two or three plates (sky reflection, body, the dark band under quays and boats), with the lights' columns as the accents. Ripple detail lives only near the camera, faded by `OS_Near` as the stone's marks are.

### Streams, waterfalls, puddles and wet ground

**Flow maps.** Valve's water in Portal 2 and Left 4 Dead 2 (Vlachos, SIGGRAPH 2010) distorts a normal map along a 2D flow map at about 4 texels a metre. It runs two layers half a cycle apart, so each restart hides under the other, with noise to break the pulsing and an offset to break repetition. The flow maps were "combed" in Houdini from level geometry; normals weaken where flow is fast; debris flows by a shifted range. Playtesters "took 17% fewer wrong turns" with flowing water. Far Cry 5 generates rivers, lakes and waterfalls from splines, with banks and terrain textures, and its water mask feeds the vegetation (secondary). Sea of Thieves projects the depth buffer onto its waterfall and stream meshes, so a character cuts the falling water and raises foam at its feet. A small fall where a stream drops over a ledge is the same flowed surface turned down the rock, with foam at its foot and spray that wets the rock beside it. Our flow comes from the land. Flow direction and accumulation over the height field (`water.py` does it per part today) give each stream its flow map: the stream down Millbrook Dell, and the gully streams under the old town.

**Puddles and wet ground.** On paving, puddles already lie in the worn hollows (`Water.hlsl`). On the land, water gathers in depressions, which a depression-filling pass finds exactly. Priority-Flood (Barnes, Lehman and Mulla 2014) floods a height field inwards from its edges with a priority queue, in about twenty lines of pseudocode. The filled depth is how deep a puddle can be. Wetness between rains follows the topographic wetness index, ln(a / tan β), where a is the upslope area draining through a point and β its slope (Beven and Kirkby 1979). The index is sensitive to resolution and method (Quinn and colleagues 1995, secondary). Wildlands drew puddles by flattening the normal and overriding the albedo inside the puddle mask. RDR2's mud map shows the same for tracks.

### Quays meeting water, and boats

The tide band is narrow here: Stavanger's average spring range is about 46 cm (a harbour description on Kartverket's domain, secondary). Storm surge comes with strong wind and low pressure in the winter half-year (met.no), and adds to it (heights not found). On a quay wall the band from mean low water to the top of the splash is where the history of the water reads: wet and dark below, a black lichen band just above high water, weed in the tidal band beneath it.

| Height | What lives there | Source |
| --- | --- | --- |
| above high water, in spray | grey lichens (*Ramalina*, *Lecanora*), then yellow *Xanthoria*, orange *Caloplaca* lower; wider with exposure, narrow and blurred in shelter | MarLIN |
| just above high water | black *Verrucaria* (*Hydropunctaria*) band | MarLIN |
| top of the shore | channelled wrack (*sauetang*), then spiral wrack | SNL |
| middle | bladder wrack; knotted wrack (*grisetang*) on sheltered shores, between bladder and serrated wrack | SNL |
| low | serrated wrack (*sagtang*), then kelp below low water | SNL |
| on quay walls | barnacles and mussels in the band; green weed where fresh water runs in | (unverified) |

The lichen bands reach tens of metres up on exposed coasts and about a metre in sheltered places (`docs/research/vegetation.md`, from MarLIN: "the vertical extent of the supralittoral increases with increasing wave and wind exposure"). So in the Basin all the bands crowd into a metre or two, while the Bluff's foot and the skerries, open to the Roads, carry several metres of them (ours). The tide's level at the hour is a fact from the date (astronomical, like the sun), so the wet line on the quay and the depth under the boats move through the day.

Boats sit on the water by analytic heights: three or four points sampled from the same Gerstner sum the shader draws, as Boat Attack's buoyancy does. Moored boats roll a little with the Roads' longer waves at the Basin's mouth and hardly at all at its head.

## 4. Coast and beach

The coast in `centre_land.py` already says what each stretch is: "q" a quay, "n" natural rock and shingle, "b" beach. Each becomes a kind.

- **Natural rock shore.** Svaberg slabs dipping into the water, joints and gullies across them, the zonation bands above, wrack below, rock pools in hollows (Priority-Flood again). Spray and exposure set the band heights.
- **Shingle.** Steep faces, around 1:5 for coarse sediment against about 1:100 for fine sand (King 1972, via the UK coastal geomorphology review, secondary); a berm where storms throw it; rounded stones. Cannery Bight's head has a shingle beach where the stream comes in.
- **Sand.** Bonfire Beach at Slipway Cove's head, sheltered, facing north-west: a gentle face, a wet swash band that darkens and shines, ripple marks, the drift line.
- **Wrack and kelp.** Cast-up kelp lies in banks after storms and was once carted off for fertiliser (`docs/research/vegetation.md`). A storm is an event with a date; the bank it leaves rots and is cleared or not.
- **Salt and wind.** Salt deposition drops steeply over the first few hundred metres from the coast, then declines weakly and irregularly (a Dutch dune review, secondary); spray reaches higher on exposed shores. The living fabric's wind and salt field (`docs/living-fabric.md`) should take distance to open water weighted by fetch and height, with shelter from the land and buildings. It drives the lichen bands, rust, chalking paint, tree lean and the heath's wind-cut edge.

## 5. Made ground in a town

### The land as a record

Towns grow onto the water by filling it. Bryggen's waterfront moved roughly 140 m out from the medieval shore (travel sources, secondary); Museum Stavanger's yearbook studied when the inner Vågen was filled and when its quays and piers were built (Kvitrud 2018, secondary: the article would not open). A quay is a wall with fill behind it; a quay apron is made ground at a set height over the water (ours stand about two metres over it, `heart_layout.py`). Lanes are cut into the slope and built out over it; yards are terraces held by walls; house plinths take up the slope; a road tunnel's portal is a blasted cut. Dishonored 2 wrote the landmass into its backstory; the town system (`docs/town-system.md`) already treats "land and old lines" as the frame every plan unit is laid on.

### How the land meets what is built on it

Every height difference on screen needs a maker. The clay's banks along lanes already follow two slopes (`heart_layout.carve`: a fall of 0.75 below, 0.95 above). The rules, by what holds the step:

| Step | Made by | Shape | When |
| --- | --- | --- | --- |
| up to about 0.3 m | the ground itself | a soft bank or a kerb | anywhere |
| soil, a bank | a cut or fill left to grass | at most the talus angle for soil, about 1:1.5 (unverified for Norwegian practice) | outside the dense town; fill behind quays before the wall |
| a wall | dry stone, later mortared, later concrete | battered about 3:1 (`docs/research/stone.md`), stones by era | yards, lanes, terraces, quay edges |
| rock, cut | blasting | near vertical, drill marks by era | where the lane met the knuckle; road cuts; portals |
| rock, natural | left standing | its own planes | where it was too hard to cut |
| a stair or a plinth | the stone and house kinds | by era | doors above lanes; houses on slopes |

At every foot the water field gathers: damp, splash, moss, gravel and weeds (`docs/foundations.md`). The ground never runs smoothly up a wall's face; it stops at the wall's foot along a breakline.

### How games and tools fit towns onto slopes

CityEngine aligns terrain to shapes (raise below, lower above, a border band with easing) and keeps the original height map untouched, writing the change as "a separate elevation delta image", with cut and fill volumes in some versions (Esri documentation). Tiny Glade's buildings first stuck to the terrain, then gained an elevation system that had to handle support and overlap. Cities: Skylines II players complain of "ugly steep terrain steps" under buildings on slopes (forum, secondary): the failure of flattening without a maker. Townscaper's lesson, from `docs/research/stone.md`, is that the design is in the transitions.

Real towns on this coast do it with plinths of dry stone to the lowest ground, cellars on the low side, rock cut behind on the high side, terraces held by walls, and lanes along the contours with stairs down the gullies (`docs/town-plan.md`). The clay already does this in one undated pass (`carve`, `ground_walls`); the change is to date each act and give each its edge.

## 6. For us

### The land as a building block

The land joins the system the way every kind does (`docs/systems.md`, How a new thing joins): facts, a generator, parts, shared layers, tiers. It has four layers of data.

**Natural ground (the pack).** What stood before the first act (`docs/town-system.md`, "The frame").

| Layer | What it holds | From |
| --- | --- | --- |
| bedrock surface | the rock's height | the designed contours and spot heights (`centre_land.py`), landforms as vectors |
| regolith | thickness and kind over the rock: moraine, peat, sand, shingle, beach sand | rules from slope, wetness and the moraine's extent |
| landforms | knolls, cliffs, outcrops, skerries as outlines with rock kind, ice vector, foliation strike and dip, joint sets | the pack, drawn by hand as now |
| water | sea level and tide, lakes, streams' lines, the seabed | the coast polygons, a bathymetry rule (shelving rock, sand, dredged quays) |

**Made-ground acts (dated).** Each act is a record like any thing's (`docs/living-fabric.md`). It holds an outline or a line; its kind (fill, cut, terrace, bank, quay apron, dredge, blast, portal); its target surface (a plane, a ramp, a lane's profile); its edge treatment (a wall kind and era, a bank angle, a cut with its drill era); its year; and its founder (the plan unit). The ground in a year is the natural ground plus every act up to that year, applied in date order, as CityEngine applies its deltas. Today's `carve()` becomes the first set of acts, with years from the town system's units. A cut leaves rock bare from its year (lichen, drill marks); a fill leaves made ground (weeds, nettles where phosphate is, settling); a bank turfs over the years after it.

**Fields (baked per chunk).** Generated from the two layers above and from the town, at 0.5 to 1 m in the heart and 2 to 4 m beyond, stored in textures per chunk as `performance-at-scale.md` plans:

| Field | Computed from | Read by |
| --- | --- | --- |
| soil depth | regolith, acts | nature (bare rock, heath, turf, trees), the ground shader, turf edges |
| rock exposure and years bare | landforms, cuts | growth (lichen size), the rock shader |
| flow and accumulation | the ground's height (D8 or better) | streams, run-off streaks, gullies' damp, flow maps |
| depressions | Priority-Flood fill depth | puddles, rock pools, bog |
| wetness | topographic wetness index, plus springs and stream lines | moss, rushes, bog, mud, the ground's darkness |
| wind and salt | fetch-weighted distance to open water, height, shelter | lichen bands, tree lean, heath's edge, rust, paint |
| sun dose and sky | the sky map, a sun-dose bake (`history-in-things.md`) | growth, drying, the ground's value |
| made ground | the acts | material choice (fill, rubble, garden soil), weeds |
| feet | the feet field | paths, wear in turf, bare soil |

**Parts (placed from vectors).** Natural stone (outcrops, ledges, faces, boulders, shore slabs) from the rock generator; walls, quay walls, stairs, kerbs and paving from the stone kinds; the shore kinds; water bodies. Every part with an edge on the ground adds its foot line as a breakline.

How it joins the rest:

- **Stone.** Natural stone is a stone material with its own rules (the pack's bedrock kinds); it takes the same history layers (lichen, moss, stains, water). Walls and quays are made stone; they stand on the ground's breaklines and read the ground map at their foot.
- **Paving.** Paving is laid stone over the ground; the ground under it is cut away. The lane's profile is a made-ground act; the paving is its surface.
- **Nature.** Every plant community reads the fields (`docs/nature.md`); the ground shader draws the communities' far colour from the same mix, so the far land is the colour of what grows on it.
- **Water.** The water layer on surfaces (`Water.hlsl`) and the water bodies share the weather; the tide band writes into the quay's water bake.

### Geometry: a height field plus parts

- Chunks of 64 m (Far Cry 5's sector size), each a constrained triangulation: grid points inside, breaklines along every wall foot, kerb, quay line, rock outline and lane edge, triangles removed under paving and houses.
- Rings: about 0.5 m within 64 m, 2 m to 256 m, 8 m to 1 km, 64 m to the horizon; skirts between rings, as the clay's `skirt()` does now; a coarse shadow caster per chunk (Firewatch).
- Natural stone as parts with their own tiers (`materials-at-scale.md`: full within 5 m, a third to 20 m, a quarter beyond, merged far), sunk into the soil depth.
- The far land: the 64 m mesh with a baked colour from the fields per season, and the strata tint trick from Far Cry 5 (rock tint written onto the ground under every unloaded rock part).

### What the clay land should become, in order

1. Split the land's data (`centre_land.py`): bedrock, regolith, landforms with rock kind and vectors, water and seabed, as layers rather than one `heights()`. Same shapes as today; the clay frames should not change. This is where the pack's ice direction and foliation are written down.
2. Date the acts (`heart_layout.carve`, `ground_walls`): every lane cut, yard, pad, quay apron and wall as an act with a year and an edge. The corner first: the lane cut past the knuckle in the 1870s, D's yard, the quay below.
3. Breaklines and chunks (`heart_build.ground_mesh`): replace the regular 1.5 m grid with chunked triangulations that stop at hard edges. Fixes the quay saw-teeth (a known clay fault in `NOW.md`) and the knoll's steps at once, because the quay walls and ledges become parts.
4. The corner's knuckle as the first natural-stone part (plan step 3): built from the town's rock kind and the three vectors, a dated cut face to the lane, judged alone in grey light and in the corner's three lights, then the heath above E on the soil depth field.
5. The fields, baked for the heart: soil depth, flow, depressions, wetness, wind and salt, made ground. Checked as maps before anything reads them.
6. Quay edges and the Basin's water (plan step 6): quay walls as stone along every "q" stretch, the water body from the coast polygon with baked depth and shore distance, the Gerstner sum from the hour's wind.
7. Watch Knoll and the Bluff: the soft back as height field, ledges along the strike as parts, the Crack as a joint, the Bluff's face and talus.
8. Shore kinds: natural rock with bands, Cannery Bight's shingle, Bonfire Beach's sand.
9. The ground shader: few materials from the fields with crisp edges, then the far colour bake.

### Water and coast in URP at our budgets

| Part | Approach | Cost |
| --- | --- | --- |
| Water bodies | meshes from the coast and lake polygons with baked depth, seabed colour, shore distance and exposure; dense near the camera, coarse far | under 100,000 triangles in view (ours, unmeasured) |
| Waves | 8 to 12 Gerstner waves per body, sized from wind and fetch; geometry only in the near ring and in the Roads; two hex-tiled detail normal maps; rain rings in drizzle | a few dozen ALU per pixel; CPU heights for boats for free |
| Colour | opaque; body colour from baked depth and seabed; reflection by Fresnel | no refraction pass |
| Reflection | URP SSR (already on), sky probe fallback; a small planar reflection of masses only if SSR fails the eye-level test | SSR already paid; planar to be measured before it is used |
| Lights on water | columns drawn from the nearest lamps and windows in the lights list, stretched by the wind's slope spread | a short loop per pixel near lit water |
| Foam | baked shore distance with exposure; boats live; the Basin almost none | small |
| Tide | level from the date and hour; the quay's wet band and weed from the water bake | none at run time |
| Wakes | the ferry's wake as a fading decal on its route | small |
| Fog | the existing sea fog bank lies on all of it | already paid |

## What we should do

Ranked by what each moves toward the corner and the heart at the city view. Days are working days for Claude at the current pace, before review, as in `materials-at-scale.md`.

| # | Change | Cost | What it buys |
| --- | --- | --- | --- |
| 1 | **Write the pack's land facts:** the town's bedrock kind (see below), one ice direction, the foliation's strike and dip, two or three joint sets with spacing, the tide's constants, the seabed rule; record them in the setting pack | half a day | every rock and knoll obeys the same reasons; the knoll's shape gets its cause |
| 2 | **Split the land into layers and dated acts** (`centre_land.py`, `heart_layout.carve`): natural ground plus acts with years and edge treatments, applied in order; same clay frames | 2 days | the land joins the living fabric; years sheets of the corner can show the 1870s cut and each yard's making; rock bare-since years for lichen |
| 3 | **The rock generator and the corner's knuckle:** a natural-stone part cut by joint sets, leaned by foliation, smoothed and plucked by the ice vector, chamfered by kind; a dated cut face with its era's drill marks; history maps; judged alone in grey light, then in the corner | 4 to 5 days | the "concrete slab" knuckle becomes rock; the first of every outcrop, ledge and face in town |
| 4 | **Chunked ground with breaklines** in `heart_build.py`: constrained triangulation per 64 m chunk, rings, skirts, coarse casters | 3 days | quay saw-teeth and knoll steps gone; ground stops cleanly at walls; land at about 370,000 triangles for the whole view |
| 5 | **The land's fields:** soil depth, flow, Priority-Flood depressions, wetness index, wind and salt, made ground, per chunk; shown as map sheets | 2 to 3 days | nature, growth, puddles and the ground shader all read the same truth; plan step 3's heath and moss have somewhere to grow |
| 6 | **The water body and shader:** meshes from the coast with baked depth, seabed and shore distance; Gerstner sum from wind and fetch; body colour by depth; SSR; boats' heights on the CPU; judged at eye level, the street stop, 35 m and near-isometric in drizzle, low sun and blue hour | 4 days | the Basin reads as water from every stop; the fog and lamps have a true surface to lie on |
| 7 | **Light columns on the water** from the lights list, stretched by the wind | 1 to 2 days | Hasui's night harbour from facts; the strongest accent in the corner's camera 2 at blue hour |
| 8 | **Quay walls along every "q" stretch** with the tide band, lichen and weed zones from the water bake | 3 days (with the stone kind) | the town's edge reads from the city camera; the known clay fault closed |
| 9 | **Watch Knoll and the Bluff:** ledge and face kits laid along the strike, talus by thermal erosion on the soil layer, the Crack | 3 to 4 days | the town's landmark rock holds from the far stop to the Crack at eye level |
| 10 | **The ground shader:** few materials chosen from the fields, hex-tiled, crisp community edges, the ground map that rocks and walls read at their foot; the far colour bake | 3 days | the land between things looks made with care; the far land is the colour of what grows on it |
| 11 | **Shore kinds:** rock shore with bands, shingle, sand with swash band and wrack lines as storm events | 3 days | the coast reads as this coast; Bonfire Beach and Cannery Bight become places |
| 12 | **Streams and flow maps** from the flow field; Millbrook Dell's stream and the gully streams | 2 days | water that shows the way, as Valve measured |
| 13 | **Planar reflection test**, only if SSR fails at the eye-level harbour views: masses only, small target, measured on the corner's frame time | 1 day | an evidence-based answer instead of a guess |

Items 1 to 5 belong to plan step 3 (the corner's ground), with the fields baked for the corner first. Items 6 to 9 belong to plan step 6 (the heart at the city view), though the corner's camera 2 will want the Basin's water early. Item 2 should land before the corner's years sheet (plan step 4).

## For Øystein to decide

1. **The town's bedrock: Stavanger's phyllite, or the gneiss of the reference photographs.** Phyllite is the truth of the place (NGU): laminated, banded grey-green and graphite-black, rusty in places, splitting into thin ledges, matching the slaty stone of the old town's walls and steps (`docs/references/stone/` 02, 03). The photographs of bedrock on the board (04, 10, 16) are of Ålesund's gneiss and a Bergen road cut: paler rock in broad, smooth slabs. Phyllite makes a darker, more striped town rock; gneiss a lighter, calmer one. We propose phyllite for the town's knolls and the Bluff, gneiss and granite for erratic boulders and imported dressed stone, and a reference board of Stavanger's own rock (needs your OK to download).
2. **A water reference board** (needs your OK to download): Hasui's water prints, Grimshaw's harbours, Norwegian harbour photographs in drizzle and at blue hour, and views of harbour water from above, so the water's target is set before item 6.

The rest (the knoll's orientation against the ice, planar reflections or not, the fields' resolutions) can be decided on analysis under the delegation of 22 October.

## Gaps

- Primary sources that would not open: the talks on Ghost of Tsushima's landscapes (Pohlmann), The Witcher 3's terrain (Gollent), Breath of the Wild's field design (CEDEC 2017), Battlefront's photogrammetry and Brucks's distance fields; the artstation pages of Ghost of Tsushima's terrain team; Kvitrud's article on the inner Vågen; the VMFA's Hasui text. Far Cry 5 rests on notes by a third party. No terrain or water talk from Rockstar, and nothing primary on the water of Firewatch or Breath of the Wild.
- Facts not settled: the ice-flow direction at Stavanger (sources conflict); the phyllite's dip; whether the real knolls (Valberget is about 21 m, a local wiki says, secondary) are phyllite outcrops or till-covered; Stavanger's mean and storm water levels from Kartverket's own tables; when presplitting came to Norway; Norwegian bank angles for soil cuts and fills (the road handbook's chapters did not open); quay construction by era in Stavanger (timber cribs, dry stone, granite, concrete, sheet piling).
- Not measured: the cost of URP SSR on the Basin at our frame; the cost of a small planar reflection; the triangle counts of chunked ground with breaklines (estimated only); how far the knoll's ledges can be height field before they must be parts.
- No craft source found for how games fit dense towns onto steep slopes beyond flattening, foundations and CityEngine's deltas; the best evidence is the real towns.
- Not yet studied: snow and ice on the land and in the harbour (with weather and seasons, plan step 9), sound of water (scenes), and the underwater view, which the camera should probably never show.

## Sources

Terrain research: Galin, Guérin, Peytavie, Cordonnier, Cani, Benes and Gain, [A Review of Digital Terrain Modeling](https://www.cs.purdue.edu/homes/bbenes/papers/Galin19CGF.pdf), Eurographics STAR 2019 · Peytavie et al., [Arches](https://perso.liris.cnrs.fr/egalin/Articles/2009-arches.pdf), 2009 · Cordonnier, Jouvet et al., [Forming Terrains by Glacial Erosion](https://cs.purdue.edu/cgvlab/www/publications/Cordonnier_2023_ToG), SIGGRAPH 2023 · Barnes, Lehman and Mulla, [Priority-Flood](https://arxiv.org/pdf/1511.04463), 2014 · Beven and Kirkby's wetness index, via [SAGA's documentation](https://saga-gis.sourceforge.io/saga_tool_doc/9.3.0/ta_hydrology_20.html) and [HESS 2021](https://hess.copernicus.org/articles/25/527/2021/) · Esri, [Breaklines in surface modelling](https://desktop.arcgis.com/en/arcmap/latest/extensions/3d-analyst/breaklines-in-surface-modeling.htm) · Imhof's aerial perspective, via [Jenny and Patterson](https://shadedrelief.com/articles.html) (secondary).

Tools: SideFX, [HeightField Erode](https://www.sidefx.com/docs/houdini/nodes/sop/heightfield_erode.html) · Unity, [Terrain erosion](https://docs.unity3d.com/Manual/terrain-Erosion.html), [thermal](https://docs.unity3d.com/Manual/terrain-Erosion-Thermal.html), [Terrain Lit](https://docs.unity3d.com/6000.3/Documentation/Manual/urp/shader-terrain-lit.html), [Terrain Layers](https://docs.unity.com/en-us/engine/6000.3/manual/creating-environments/script-terrain/terrain-textures/class-terrain-layer), [Paint Holes](https://docs.unity3d.com/Manual/terrain-PaintHoles.html), [TerrainData](https://docs.unity3d.com/ja/6000.0/ScriptReference/TerrainData.html), [GPU Resident Drawer](https://docs.unity3d.com/6000.0/Documentation/Manual/urp/gpu-resident-drawer.html) · QuadSpinner, [Gaea download and licence](https://quadspinner.com/Download) · Esri, [CityEngine: Align terrain to shapes](https://doc.arcgis.com/en/cityengine/2024.1/help/help-align-terrain-shapes.htm) · Terrain3D, [control map format](https://terrain3d.readthedocs.io/en/latest/docs/controlmap_format.html) (secondary for The Witcher 3) · Mikkelsen, [Practical Real-Time Hex-Tiling](https://jcgt.org/published/0011/03/05/paper.pdf), JCGT 2022.

Games: van Muijden, [GPU-Based Procedural Placement in Horizon Zero Dawn](https://www.guerrilla-games.com/media/News/Files/GDC2017_VanMuijden_GPUBasedProceduralPlacementInHorizonZeroDawn.pdf), GDC 2017 · Pohlmann, [Samurai Landscapes](https://gdcvault.com/play/1027352/Samurai-Landscapes-Building-and-Rendering), GDC 2021 (abstract) · Mills, [notes on Procedural World Generation of Far Cry 5](https://christianjmills.com/posts/procedural-tools-far-cry-5-notes/) (secondary) · [Landscape and material pipeline of Ghost Recon Wildlands](https://80.lv/articles/landscape-and-material-pipeline-of-ghost-recon-wildlands/), 80.lv · [Ghost Recon Wildlands terrain talk](https://gdcvault.com/play/1024029/-Ghost-Recon-Wildlands-Terrain) and [World Machine forum](https://forum.world-machine.com/t/wm-used-in-ghost-recon-wildlands/4435) (secondary) · Gollent, [Landscape Creation and Rendering in REDengine 3](https://www.gdcvault.com/play/1020394/Landscape-Creation-and-Rendering-in), GDC 2014 (abstract) · Andersson, [Terrain Rendering in Frostbite Using Procedural Shader Splatting](https://www.advances.realtimerendering.com/s2007/Andersson-TerrainRendering(Siggraph07)-CourseNotes.pdf), SIGGRAPH 2007 · Ng, [Making the World of Firewatch](https://media.gdcvault.com/gdc2016/Presentations/Ng_Jane_MakingTheWorld.pdf), GDC 2016 · [Campo Santo blog Q&A](https://blog.camposanto.com/post/100170868639/i-asked-twitter-if-anyone-had-questions-about-the) · [The design secrets of Breath of the Wild](https://80.lv/articles/the-design-secrets-of-breath-of-the-wild/) (secondary) · [How Shedworks refined the art of Sable](https://www.gamedeveloper.com/marketing/how-shedworks-refined-the-art-of-sable-in-pursuit-of-readability) (secondary) · [Tiny Glade developers on proceduralism](https://80.lv/articles/exclusive-tiny-glade-developers-discuss-bevy-proceduralism-publishers-cozy-games/), 80.lv · [Dishonored 2: Creating Karnaca](https://bethesda.net/en-AU/news/dishonored-2-creating-karnaca) · [Cities: Skylines II forum on slopes](https://steamcommunity.com/app/949230/discussions/0/3877095833476954030) (secondary) · Chahi on Another World, [GameSpot Q&A](https://www.gamespot.com/news/6164199.html) and [GDC 2011 postmortem write-up](https://www.gamedeveloper.com/game-platforms/gdc-2011-eric-chahi-s-retro-postmortem-i-another-world-i-) (secondary) · [Photogrammetry and Star Wars Battlefront](https://ea.com/frostbite/news/photogrammetry-and-star-wars-battlefront) (abstract) · [Megascans on Fab](https://www.cgchannel.com/2024/10/epic-games-has-made-megascans-free-to-all-but-only-until-the-end-of-2024/) (secondary) · Epic, [Runtime Virtual Texturing quick start](https://dev.epicgames.com/documentation/en-us/unreal-engine/runtimevirtual-texturing-quick-start-in-unreal-engine).

Water: Tessendorf, [Simulating Ocean Water](https://people.computing.clemson.edu/~jtessen/reports/papers_files/coursenotes2004.pdf) · Finch, [Effective Water Simulation from Physical Models](https://developer.nvidia.com/gpugems/gpugems/part-i-natural-effects/chapter-1-effective-water-simulation-physical-models), GPU Gems · Ang, Catling, Ciardi and Kozin, [The Technical Art of Sea of Thieves](https://history.siggraph.org/wp-content/uploads/2022/09/2018-Talks-Ang_The-Technical-Art-of-Sea-of-Thieves.pdf), SIGGRAPH 2018 · [Crest](https://github.com/wave-harmonic/crest) · Unity, [Boat Attack](https://github.com/Unity-Technologies/BoatAttack) and [the HDRP water system](https://unity.com/blog/engine-platform/new-hdrp-water-system-in-2022-lts-and-2023-1) (secondary) · Unity, [Preview of Screen Space Reflections for URP](https://discussions.unity.com/t/preview-of-screen-space-reflections-for-urp/1721494) · Courrèges, [GTA V graphics study, part 2](https://www.adriancourreges.com/blog/2015/11/02/gta-v-graphics-study-part-2/) (secondary) · Stachowiak, [Stochastic Screen-Space Reflections](https://www.ea.com/frostbite/news/stochastic-screen-space-reflections), SIGGRAPH 2015 (abstract) · Minnaert's light pillars, via [Stanford course notes](https://graphics.stanford.edu/courses/cs99d-99/AshleyRich/AshleyRich.html) and [Colorado physics demos](https://physicslabs.colorado.edu/demos/optics/geometrical-optics/reflection-from-flat-surfaces/rippled-reflection/) (secondary) · Vlachos, [Water Flow in Portal 2](https://alex.vlachos.com/graphics/Vlachos-SIGGRAPH10-WaterFlow.pdf), SIGGRAPH 2010 · Texel Raptor, [Croakwood devlog 5: water](https://www.texelraptor.com/blog/croakwood-devlog-5) · Brucks, [Distance Fields and Shader Simulation Tricks](https://gdcvault.com/play/1025945/Technical-Artist-Bootcamp-Distance-Fields), GDC 2019 (abstract) · Coastal Engineering Manual formulas via [planetcalc](https://planetcalc.com/4442) (secondary).

Painters: LACMA collection records for Kawase Hasui: [Nagare Pleasure Quarter, Kanazawa](https://collections.lacma.org/object/87628), [Izumo, Matsue (Hazy Moon)](https://collections.lacma.org/object/29654), [Shirosaki, Tajima](https://collections.lacma.org/object/88180), [Evening in Atami](https://collections.lacma.org/object/87777) · [Sotheby's on a Kinosaki print](https://www.sothebys.com/en/buy/auction/2026/arts-dasie/kawase-hasui-1883-1957-kinosaki-tajima-taisho) (secondary) · Gurney, [Why I love overcast light](https://jamesgurney.substack.com/p/why-i-love-overcast-light) (secondary) · `docs/references/stone/` 17 to 20.

Land and coast facts: NGU, [Karakterisering av fyllitt og byjord i Stavanger](https://static.ngu.no/upload/Publikasjoner/Rapporter/2024/2024_034.pdf), report 2024/034 · Statsforvalteren i Rogaland on sulphide-rich phyllite (search summary only; the page had moved, secondary) · SNL, [svaberg](https://snl.no/svaberg), [rundsva](https://snl.no/rundsva), [strandflate](https://snl.no/strandflate), [fyllitt](https://snl.no/fyllitt), [brunalger](https://snl.no/brunalger), [grisetang](https://snl.no/grisetang) · MarLIN, [yellow and grey lichens on supralittoral rock](https://www.marlin.ac.uk/habitats/detail/96) · joint control of roches moutonnées: [Krabbendam and Glasser on NW Scotland](https://research.aber.ac.uk/en/publications/glacial-erosion-and-bedrock-properties-in-nw-scotland-abrasion-an/), [Rastas and Seppälä via Cambridge](https://resolve.cambridge.org/core/journals/annals-of-glaciology/article/rock-jointing-and-abrasion-forms-on-roches-moutonnees-sw-finland/5041AD4E83A95D68D50C1055011ACB91) (secondary) · ice flow on Jæren: [NGU Bulletin 411](https://static.ngu.no/upload/Publikasjoner/Bulletin/Bulletin411_1-55_Andersen.pdf) (secondary) · [geo365 on Norwegian rock blasting](https://geo365.no/?p=2889) · FHWA, [Context sensitive rock slope design](https://www.fhwa.dot.gov/clas/ctip/context_sensitive_rock_slope_design/ch_3_2.aspx) (secondary) · Eawag, [Tintenstrich communities](https://www.eawag.ch/en/department/uchem/projects/translate-to-english-cyanolichen) (secondary) · Kartverket, [Vannstand og tidevann Stavanger](https://opencom.no/en_GB/dataset/vannstand-stavanger-kartverket) and the [Stavanger harbour description](https://dnl.kartverket.no/api/ogc/v1/collections/dennorskelos/place/items/5a6b2219-f2ca-4eac-81e1-ebbe16c1137a?f=html) (secondary) · met.no, fact sheet on water level (no figures) · JNCC, [Coastal geomorphology of Great Britain, chapter 5](https://data.jncc.gov.uk/data/118b87ed-d7dd-4ea0-99ad-36ed62d2eab0/gcr-v28-coastal-geomorphology-c5.pdf) (secondary) · salt spray: [Dutch dune review](https://natuurtijdschriften.nl/pub/539583/ABN1969018002002.pdf) (secondary) · Bryggen: [Lonely Planet](https://www.lonelyplanet.com/pois/1292163) (secondary) · Kvitrud, [De indre delene av Vågen](https://www.museumstavanger.no/uploads/arbok/2019-2015/2018-ARNE-KVITRUD-De-indre-delene-av-Vågen-i-Stavanger-fra-middelalderen-til-tidllig-på-1600-tallet.pdf) (would not open) · [Valberget](https://lokalhistoriewiki.no/wiki/Valberget_(vei_i_Stavanger)), lokalhistoriewiki (secondary).
