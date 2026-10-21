# Stone: how the best build it, and what it does over the years

Research for the stone system (`docs/stone.md`), October 2026: what shipped games and painters do with stone, and the facts of Norwegian steps, walls, paving and quays that the generator reads. Claims from summaries or forums are marked (secondary); claims not confirmed, or our own arithmetic, are marked (unverified).

## The bottom line

- History is drawn from causes, never from texture. A tread's hollow is footfall times years over the stone's hardness (Archard's law); lichen's size is its growth rate times the years since the stone was bare or cleaned; a relaid step is a dated event. Then every mark is a fact, as the trees' bark marks are.
- Minimum information, big shapes first (The Witness: "minimize the amount of noise"; Oga: get the essential point across). Each stone has a real chamfer of its own size, two or three values, and detail only where the story is: the lit edge, the worn middle, the damp foot.
- A few stone kinds and a few kinds of piece, laid by real rules: steps rest on the step below, walls bridge every joint and lean back, setts run in arcs. Every piece its own seeded instance, so nothing repeats.
- One stack of history layers, the same for every hard surface (stone, later brick, render, concrete, asphalt): wear and polish, stains, growth, damage, repair, wet. Masks from geometry and facts: occlusion and shade for moss, gravity flow for stains, a footfall map for polish.
- Value painted into the pigment, real relief kept, shade from the light (the town's one shade rule). No scanned textures with light baked in.
- Wet is a state: granite darkens and glosses, water stands in the worn hollows (they are the puddles), and the gloss dries before the dark.

## How games build stone

- **Firewatch.** Rocks sculpted in ZBrush, normals baked, textures made in Photoshop; Olly Moss painted over textures for a more painterly pass, and over screenshots of the blockout; lighting matched to his paintovers with atmospheric volumes. Art judged in the game under different lights: "A beautiful looking flat texture might not look great in game" (Campo Santo blog). From reports of Jane Ng's talk: flat shapes, strong silhouettes, colour in bands for depth, texture detail only on objects that matter to the story (secondary).
- **The Witness.** "Minimize the amount of noise", "simplified reality": the minimum that tells you what a thing is; chipping a cube's edges is enough to read as stone (secondary).
- **Townscaper.** The design is in the transitions: what happens where shapes change (a corner, a wall meeting a roof); garden walls appear at corners and where colours change. Ornate detail looks cluttered from a raised view.
- **Sable, Tunic.** Flat shading loses depth; it is won back with light, fog and placement that carries perspective; extra detail density looked wrong (secondary).
- **Naughty Dog.** Layered materials blended by vertex colour (cracks, moss, leaks, wet); height blending, so the second layer settles into the first's cracks; an occlusion blend as free contextual data (secondary).
- **Skyrim's kits.** Players spot repeated detail before repeated architecture; footprints in multiples of each other; numbered variants; glue pieces for transitions.
- **Trim sheets** (Sunset Overdrive): long dressed pieces (kerbs, copings) from strips with bevels in the normals.
- **Disco Elysium.** Hand-painted environment textures, each with its own height, normal and shadow maps (secondary); anything that changes with time drawn in real time, never painted in.
- **Raised cameras.** Riot calmed Summoner's Rift by clamping value ranges and controlling detail (secondary); Diablo IV built its detail around the isometric camera and puddles form in ruts and hoof prints.

## How painters paint it

- **Kazuo Oga** lays a ground layer, then works from large shapes to small; detail in small things painted on top; he studies places on site because photographs lose the atmosphere and the scale.
- **Simon Stålenhag** starts from his own photographs, sketches over them and repaints large, layer by layer, with brushstrokes, no photo texture (secondary).
- **Kawase Hasui**: wet shrine stone in the rain as reflective planes of the sky.
- **Hammershøi**'s greys are not black and white mixed: cobalt blue and other pigments are in them; a final thin grey layer softens the outlines. Grey stone in grey light is a coloured grey.
- **Overcast light** (James Gurney): less contrast, bigger shapes, purer colour, greyer shadows (secondary). Rocks grouped into masses, shadows blocked in first (secondary).
- Our reading (unverified): each stone in two or three values; detail on the lit edge, the worn middle and the dark foot where moss grows; joints as broken accents, never a grid.

## What stone does over the years

**The stone.** Iddefjord granite (Østfold) was quarried from the 1840s, peaking about 1913: light grey, medium-grained, sometimes faintly red, splitting in two directions at right angles; used for kerbs, setts, quay stone and building, and every big Norwegian city got "a generous dose" of it. Bergen used local gneiss and granite; Ålesund's rebuilding after 1904 largely local stone. Stavanger stands on phyllite and mica schist, fissile and poor for steps, so its step stone was likely brought in (unverified); Lysefjorden has light granites and granite gneiss (secondary). Larvikite, blue or green shimmering, went in its lower grades into walls and kerbs. Iron in biotite or pyrite rusts to yellow-brown spots; salt and wet-dry cycles lose grains; in damp climates surfaces stay humid, are colonised and blacken (Gloeocapsa's black stains); greening starts as a shift towards yellow-green on shaded wall areas kept wet by run-off (secondary).

**Steps.** Block steps: each step's front rests on the back of the one below, sometimes rebated; nosings rounded, chamfered or square; treads laid with a slight fall to shed water; over a void, carried on an arch; iron handrails set in holes with poured lead, and when the lead loosens the iron rusts, frost jacks the hole, the stone cracks and stains rust (Historic Scotland). Outdoor rise 12 to 16 cm, tread 30 to 40 cm (unverified). Ålesund's 418 steps up Aksla were begun in 1885 by a town society and built over about 15 years, natural stone set into the terrain, partly slabs; most recast in concrete in 2014 to 2015, some original groups kept. Repairs, each visible: re-dressing; swapping unworn side steps into the centre or turning a step over (some nosings sharper than the rest); a stone indent in a cut pocket; a cement screed in the hollow (common, ugly, speeds decay); mortar infill left distinguishable; concrete overtreads.

**Paving and kerbs** (Oslo's record; for our town unverified). Rounded field stone with a central gutter before the 1800s; hewn stone from the 1840s; prismatic setts (about 20 by 13 cm) from about 1850; granite from Iddefjord once local stone ran out, about 1870. Kerbs 5 inches wide in 1853, 8 in 1870, 12 (30 cm) from about 1880. Granite slab pavements 30 to 42 cm wide from 1865; concrete slabs from 1909. Small setts, 10 cm cubes laid in arcs (bueform, invented 1885), in real use from 1910 and the main town surface from 1910 to 1950: arcs 1.2 to 1.6 m wide, larger stones at the crown, smaller at the joints between arcs, half-arcs meeting the kerb square; expected to last 15 years, many lasted 90. Asphalt from 1922; in 1947 half of Oslo's carriageways were still setts.

**Wear.** Granite resists abrasion five to ten times better than limestone or slate (Kessler 1933, stair treads in use; unverified as a ratio); wear is uneven on mottled stone, and damp lowers resistance. Polish comes fast: granite entrance steps lost 46% of their roughness in two years and about a fifth of their slip resistance in a few. Depth comes slowly: sixteenth-century college steps (stone not stated) worn 75 mm in the centre in 500 years, about 15 mm a century; for granite perhaps 1.5 to 3 mm a century at about 100,000 footfalls a year (unverified). Wide steps wear only in the middle; the hollows hold water and freeze. Wear is read by archaeologists for how often stairs were used, which way, in pairs or single file, and what was repaired (Leiden's Testimony of Stones).

**Growth.** Map lichen (Rhizocarpon) grows about 0.75 mm a year in maritime west Norway and 0.55 in the east (Jotunheimen; secondary), slower under 1 cm across, faster on north-west faces; a step laid in 1850 would carry patches 7 to 10 cm across by 1989 on edges no one treads, one of 1920 about 3 to 5 cm, one of 1960 under 1.5 cm (unverified). Xanthoria grows about 2.6 mm a year, 6 to 7 where moist, orange in sun and almost green in shade, where birds perch. Lecanora muralis makes pale yellow-green rosettes of 1.5 to 3.5 cm on pavements and walls and tolerates town air; Grimmia pulvinata cushions of 1 to 4 cm on wall tops; Tortula muralis is the commonest moss on mortared walls (secondary). On a quay wall: a black band of Verrucaria at the top of the tide, yellow and grey lichens above (secondary); Stavanger's tide range is only about 46 cm (secondary). Trampling kills cover fast (no plot kept half its cover after 200 passes; secondary): nothing grows on the walking line, while moss, grass and shrubs root in the joints and along the side faces.

**Walls.** Dry-stone: face battered about 3:1 (Norwegian roads authority; general practice 1:6 to 1:10), stones bedded tilting back and square to the face, every joint bridged, the largest stones lowest, through-stones, flat slab copings. An undrained wall bulges, its lower part vertical or leaning out; Bergen's municipal walls slide at the top, shift and slip out, and are rebuilt in new stone. Norway made its own cement from about 1890, so mortared and concrete walls are plausible from then (unverified); wall-rue ferns grow only in lime-rich crevices, so they mark lime mortar.

## Why stone in games looks cheap

- Tiling: fixed by a random offset per tile, Voronoi blending or a hashed choice of variants (Íñigo Quílez); stochastic and hex tiling keep contrast that plain blending washes out.
- Every edge chipped the same: wear that does not follow contact and use reads as a filter.
- Bevels only in the normal map: the silhouette stays sharp; a real chamfer with weighted normals shades better.
- Grout too regular: real walls bridge every joint, put big stones low, lean back and carry through-stones.
- Uniform noise: repeated detail is spotted before repeated form.

## Distance and performance

Unity's GPU Resident Drawer instances shared meshes (Forward+ and compute shaders), best when many objects share a mesh, so stone pieces are shared meshes with per-instance data. Decals with rendering layers add a depth-normal prepass. Far off, walls and flights merge into proxies (Kena merged distant meshes; Naughty Dog's Building Proxy); octahedral impostors cost memory per unique object.

## Sources

Games: Campo Santo blog (blog.camposanto.com/post/100170868639); The Art of the Witness, GDC 2014 (artofluis.com); How Townscaper works (gamedeveloper.com); How Shedworks refined the art of Sable (gamedeveloper.com); Skyrim's modular approach (gamedeveloper.com); The Ultimate Trim (GDC Vault 1022323); Disco Elysium art (mcvuk.com); Diablo IV quarterly update, March 2022 (news.blizzard.com). Painters: Animation Obsessive on Kazuo Oga; Open Culture on Oga's process; the Vilhelm Hammershøi digital archive (pure.kb.dk); Brooklyn Museum and LACMA for Hasui. Rendering: Dorsey et al., Modeling and Rendering of Weathered Stone, SIGGRAPH 1999; Dorsey, Pedersen and Hanrahan, Flow and Changes in Appearance, 1996; Chen et al., γ-ton tracing, 2005; Desbenoit et al., lichen, 2004; Sébastien Lagarde, Water drop series (seblagarde.wordpress.com); Íñigo Quílez, texture repetition. Facts: lokalhistoriewiki.no (Gamle Stavanger; Vei- og gatedekker); snl.no (smau, brolegging, wienermønster, iddefjordsgranitt, larvikitt, murburkne, tidevann); Riksantikvaren, Rehabilitering av historisk trappeanlegg (Aksla); Historic Scotland INFORM, Exterior Masonry Steps, 2014; Kessler 1933, NBS RP612 (nvlpubs.nist.gov); EGU 2013 and 2019 abstracts on polish and slip; Matthews 2005, The Holocene; Bradwell and Armstrong 2007 (nora.nerc.ac.uk); British Lichen Society, Lecanora muralis; MarLIN, rocky shore lichen bands; Statens vegvesen on dry-stone walls (dokument.vegvesen.no); Bergen kommune, reparerer murer; conservationhandbooks.com and lowimpact.org on dry-stone walling.
