# History in things

Research for the living fabric and the shared surface layers (`docs/living-fabric.md`, `docs/foundations.md`), October 2026: how masters in games, graphics research, film, scale modelling, painting and building conservation make things and places carry their past, so that a viewer reads it and is right. It serves criterion 1 in `CLAUDE.md` (a viewer can say which parts are old, changed or neglected, and is right). Three sibling studies cover how materials are built (`materials-at-scale.md`), kits and generation (`kits-and-generation.md`) and performance (`performance-at-scale.md`); this one is about what the marks mean and how they are caused.

Sources were read in full where they opened: the graphics papers (Dorsey 1996 and 1999, Chen 2005, Gu 2006, Lu 2007), Naughty Dog's Uncharted 4 slides, Ruskin and Morris. Interviews and studies were read through their own pages. Claims taken from a search summary or a third party's description are marked (secondary); claims no source confirmed, and our own readings, (unverified). Quotations are kept to the public-domain texts; the rest is paraphrased.

## The bottom line

- Every mark has a source, a path and an age. The research models that work (water particles, γ-tons, captured context) all trace a mark from where it came from, along how it travelled, to where it stopped. Games mostly skip the source and the path and keep only the place (dirt in every crevice), which is why generic weathering reads as texture and says nothing.
- Water both cleans and stains. Most readable patterns on a facade come from the contrast between washed faces and sheltered or deposit zones.
- One process, one curve. Measured ageing (rust, drying, burning, decay) follows one curve per process; the pattern on a surface comes from each point running along that curve at its own rate and from its own start. Our "years since reset" is half of this; the per-point rate is the other half.
- Order by time. Modellers lay effects in the order the vehicle met them; archaeologists read buildings by what lies over and what cuts what. A newer mark sits over an older one, and a repair cuts what was there before it. Readers can follow this, and the system must never break it.
- The form comes first. Ruskin's lower picturesque, Naughty Dog's warning against foliage and wreckage as fluff, the modellers' "if you can see the technique it is overdone": weathering that hides what a thing is turns it into decoration.
- Parts date a place; surfaces age it. People tell old from new at a glance but date poorly from surfaces (36 per cent right on decades from photos of real houses). The era of an installed part (a window type, a sign, a plate) is what dates. Age value reads to everyone; historical value needs the specific dated part.
- Readers infer more than is there. Players turned a bug into a sandstorm that ended a village, and read one chair beside three place settings as missing chairs. Anything systematic in seeded texture will be read as history.
- Absence is evidence: no moss on the walking line, no prints in the Zone, nothing new in a city that stopped renewing.
- Our systems are missing six main things: an airborne deposit field (soot, dust, salt) with washing; stains carried from one material to another (rust, copper, lime); the splash band as its own term; the coat stack and its failure; contact wear by hands and objects on every material; and a rule and a check that newer marks sit over older ones.

## 1. Games: environmental storytelling

### What happened here

Harvey Smith and Matthias Worch's GDC 2010 talk defined environmental storytelling as staging the player's space so it can be read as a meaningful whole that furthers the narrative (the slides, read through a third-party copy; secondary). Its points that matter to us:

- The player controls the gaze, so film is a poor model. The player connects separate elements themselves, and that work builds investment.
- Build a discernible chain of events. A dead goldfish with a frozen clock and a water line tells a flood in order; one prop alone tells little.
- Echo the premise. BioShock's broken ATMs and a New Year's party gone wrong both repeat the game's theme of a society in decay.
- Systemic storytelling records the player's own history: decals and breakables that persist, and places revisited so the evidence is seen again.
- Pitfalls: a scene that implies actions the player cannot take; designers' favourite set pieces rather than the player's experience; assuming the intended reading is the one taken.

In an interview after the talk, Smith added that it has to be possible to miss things for finding them to matter, and that anonymous details waste the chance to say something (Nieman Storyboard, 2011). For us: evidence is placed by causes, never pointed at.

### Players read more than is there

Smith Nicholls and Cook studied 187 players of *Nothing Beside Remains*, a generated ruined village with no goal (2023). An out-of-place pocket watch was the bait: of 54 players who saw it, 51 examined it and 18 recorded it as their chosen object, more often than the statue or a trident. Players read it as dropped by a later visitor. One player saw a single chair beside three place settings and inferred the other chairs had been moved or destroyed. A bug at the map's edge showed blowing sand while the player was stuck; several players built it into their story (the village became unlivable because of the sandstorm), and some were sure it had been designed. The authors note the generator has no contextual understanding linking its objects; the players supplied it.

Witch Beam made the same point from the maker's side in their GDC 2022 talk on *Unpacking*: every item in a game's environment sends a message, intended or not, and item progression is character progression (Brier and Dawson, via Game Developer). Their story of one life across seven homes is told only by what is unpacked: the same objects recur, tastes shift, and a partner's flat with no room left on the shelves says more than a line of dialogue.

For us the rule in `CLAUDE.md` holds and gets sharper: seeded texture must be unsystematic at the scale of any cause. A seeded lean is texture. A seeded dark band along one side of a flight is a claim, and readers will take it as one.

### Naughty Dog: who owned it, and how did this happen

Naughty Dog's environment artists on *The Last of Us Part II* (80.lv, 2020): Anthony Vaccaro asked artists to ask how a place came to be as it is and how time and nature would reclaim it, and warned that throwing destruction, foliage and bodies into a world is fluff. Reuben Shah required that every object have a reason for the people living in the space; things from Joel's house reappear later in Ellie and Dina's farmhouse. Art director John Sweeney said the materials of a building indicate the type and severity of its decay, and that each space was given a backstory: an incident frozen in time, a place looted, someone living barricaded inside (Cook and Becker). An outsourcing studio reports being asked for the story behind each chair and window: who owned it, how it got there, what it had been through (Lemon Sky; secondary).

On the technical side the Uncharted 4 talk (Brinck and Maximov, SIGGRAPH 2016) is primary and specific. Wetness was painted by artists and drawn in four regions: a puddle's flat core; a cling zone where water shrink-wraps the surface; a saturated zone that only darkens the albedo; and dry ground. A porosity input decides how much a surface darkens when wet. Artists used it in nearly every scene. Moss got its own shading: lighter at the tips than at the base, fuzz that shows only tips at a grazing angle, wrapped light, and deep occlusion with colour added back in the dark. In *The Last of Us Part II*, weapons were worn by dirt, edge-wear and rust generators masked with grunge (80.lv).

What we take: the question "how did this happen?" asked of every mark, materials that decide the kind of decay, objects that recur with their owner (criterion 2), and Naughty Dog's wet regions as a check on `Water.hlsl`. What we leave: hand-placed backstories. Ours come from the record.

### Arkane: eras you can walk through

*Prey*'s station, Talos I, is built in layers (Engadget, 2017). The original core, built jointly by the Soviets and Americans, is cramped metal with exposed pipes and physical switches; the later owner's additions are a retro-futurist art deco. New touchscreens sit beside dusty tape decks because swapping equipment in space is expensive. Lead designer Ricardo Bare said everything in the world should have a reason for being there and for looking the way it does. This is Stewart Brand's shearing layers in a game: what is costly to change stays, and its age shows beside what was easy to change. *Dishonored 2*'s Karnaca (in `docs/living-fabric.md`) reads class through oppositions built from two centuries of backstory.

### Small houses, one family

*Gone Home* (Fullbright, 2013) tells a family through a house dense with what people leave behind. Steve Gaynor said the team set it in 1995 so that communication would still be on paper, relied on recognisable touchstones of the period, and let the player's memory fill the gaps (Game Developer). *What Remains of Edith Finch* (Giant Sparrow, 2017) stacks a family's history into the house itself: it was extended again and again, and each member's room was sealed when they died, so the house is a record by construction (secondary). *Firewatch*'s Jane Ng gave objects that matter to the story more texture detail, so detail itself signals importance (Thumbsticks, GDC 2015).

### Towns across years

*Disco Elysium*'s Martinaise still shows artillery damage and bullet holes from a failed revolution decades earlier; ZA/UM's Helen Hindpere described its architecture as mirroring its turbulent history, a mix of the 1870s and the 1970s, with a pre-revolutionary revival fallen into disarray (Film Stories). *Pentiment* shows one town in three acts years apart; Josh Sawyer said choices lead to generational changes in the community and that townsfolk remember what you did (TheGamer). Rockstar updated *Red Dead Online*'s world to match the first epilogue of *Red Dead Redemption 2*, with changes to structures, forests, railways and Armadillo (Rockstar's notice via GTABase; secondary). *Elden Ring*'s ashen capital reuses the city's structures in a later, burnt state, and its sewers and catacombs lie in layers below (game wikis; secondary).

### Subtraction, knowledge and records

*Shadow of the Colossus* removed towns, people and side quests so the empty land and its unexplained ruins carry the mood ("design by subtraction"; secondary). *Outer Wilds* makes knowledge the reward: players learn a vanished people's history by reading the writing they left (National Centre for Writing; SFRA Review; secondary). *Kentucky Route Zero* has an interlude played as a call to a tourist bureau's river guide (Kill Screen; secondary). The writing and the guide are records, the fourth kind of thing in `CLAUDE.md`: someone's account, which may be partial.

### What misleads

- Staged tableaux. Bethesda's posed skeletons became a running joke about environmental storytelling in the 2010s (Know Your Meme; Giant Bomb columns; secondary). A tableau tells one moment loudly, repeats as a formula, and has no cause in the world's systems.
- Marks without a source. The generic look of grunge in every crevice, every edge chipped and one tone of dirt everywhere.
- Anomalies with no cause. The pocket watch pulled almost every eye. An out-of-place part is a promise of a story, so it needs one.
- Decay as mood. A sad house made shabby. The engine's human test shows vivid evidence read as a verdict makes readers worse (`docs/living-fabric.md`).

| Game | What carries history | We take | We leave |
| --- | --- | --- | --- |
| BioShock, Dishonored | props and districts that echo the premise | evidence that repeats the setting's themes | authored tableaux |
| The Last of Us Part II | per-space backstories; nature's return; objects that follow their owner | "how did this happen?"; materials decide decay; recurring objects | hand-placed stories |
| Uncharted 4 | painted wetness in four regions; moss shading | the wet regions; porosity | painting by hand |
| Prey | eras of construction side by side | costly layers stay, cheap ones change | |
| Gone Home, Edith Finch, Unpacking | the house as a family's record | period touchstones; one life across homes | |
| Disco Elysium, Pentiment, RDR2 | one place in several states | years sheets; damage that stays | |
| Nothing Beside Remains | a generated ruin read by players | readers infer from anything | uncaused objects |

## 2. Weathering in graphics research

### Water: washing and staining

Dorsey, Pedersen and Hanrahan, "Flow and Changes in Appearance" (SIGGRAPH 1996), drew its phenomena from building pathology (Addleson and Rice, *Performance of Materials in Buildings*, 1991). Its argument: without rain, dirt would lie fairly evenly over walls, a little heavier near ledges such as sills, and would never be uneven enough to stain. Water makes the pattern. It picks dirt up where it runs and drops it where it slows, soaks in or evaporates. Faster flow washes cleaner. Broken streams with a slow rate stain the worst; a continuous film washes evenly. Fine dirt sticks to smooth surfaces (glass) and needs fast flow to shift.

The paper names the effects a facade shows:

| Effect | What happens | Where it shows |
| --- | --- | --- |
| Partial flow | exposed parts saturate first and run onto drier parts below, which absorb until they too overflow; dirt is redeposited where the run-off stops | a line at the end of each wash; concentrated on both sides of windows, under sills and projections |
| Differential flow | water dissolves one material and deposits it on another | white streaks from concrete or limestone on brick below; green from copper; rust from iron |
| Splashback | rain hits the ground or a ledge and throws dirt up the wall | a band at the foot of a wall, and above ledges |
| Run-off onto porous | a non-absorbent part (metal, glass) sheds its water onto porous stone or render below | heavy staining under the impervious part |
| Saturation staining | long-wet zones darken | ledges and the foot of walls |
| External sources | directional dirt from traffic or chimneys | the side facing the source; less where a building turns away |

The model drops water particles from the sky by the wind's direction (an exposure map), moves them over the surface by gravity, friction and roughness, lets them fall off at sharp edges, absorb, dissolve material and deposit it. The authors built an interactive tool so a user could guide the flows, because a physical model used for art needs control.

### Stone

Dorsey and colleagues' "Modeling and Rendering of Weathered Stone" (1999) simulated water and minerals in a thin slab under the surface. Its background catalogues what stone shows over time. In polluted rain a gypsum crust forms, takes in soot and breaks away. Horizontal and inclined surfaces erode faster than vertical ones because they hold water. Compact stone rounds its corners and loses fine detail ("corestone"). Iron in the minerals migrates out and oxidises as patchy yellow and brown. Evaporation builds a hard, weak crust, sometimes black ("black scabs"), and soluble salts bloom white (efflorescence). Most of the change sits in a graded zone near the surface.

### Where blemishes sit: accessibility and exposure

Hsu and Wong (1995) modelled dust by a surface's slope and stickiness, then corrected it by exposure to wind and by scraping from other objects. Miller (1994) computed accessibility: how easily a point can be reached by a probe, giving the tarnish left in crevices on a polished object. Wong, Ng and Heng (1997) generalised these into tendencies from geometry. Chen and colleagues later summed up this line: blemishes are strongly geometry-dependent, but these methods draw the final state directly from the geometry and do not run a process through time, so they need manual work to match nature (Chen et al. 2005).

### Sources, carriers and transport: γ-ton tracing

Chen, Xia, Wong, Tong, Bao, Guo and Shum, "Visual Simulation of Weathering by γ-ton Tracing" (SIGGRAPH 2005), traced ageing particles like photons. Each γ-ton is shot from a source (a point such as a leaking pipe, a downward area like rain, or the whole sky), travels straight, in a parabola or flowing along a surface, and settles when it runs out of energy. It carries substances (humidity, dirt, moss seed, rust) and picks them up and drops them on what it touches by simple rules. Surfaces change as they weather (rust roughens a surface, which traps more γ-tons), so the process runs in iterations.

Two of its results matter to us. Stain-bleeding: rust from an iron chain is carried by bouncing and flowing particles onto the cement staircase below and runs down its cracks. Multi-weathering: moss growing on the ground covers the soil, so less dirt splashes up the wall; growth suppresses splash. Blending two separate simulations cannot produce that interaction. The limits: each iteration took minutes, with no interactive feedback, and all effects lived in one layer, so structure (dust in the cracks of a painting) was hard.

### One curve, many rates: measured ageing

Gu, Tu, Ramamoorthi, Belhumeur, Matusik and Nayar, "Time-Varying Surface Appearance" (SIGGRAPH 2006), captured 26 samples ageing (burning wood, drying rock and cloth, rusting steel, copper patina, decaying fruit) from 16 views and 80 lights at every time step. Their factorisation found one temporal characteristic curve per process, plus static textures, and a rate and an offset at every point. The pattern on the surface arises because points move along the same curve at different rates and from different starts. It lets one transfer a process to a new surface, speed it up in chosen places (a wet footprint on a wooden floor drying faster at its edges) and extrapolate.

Wang, Tong, Lin and colleagues' appearance manifolds (2006) start from one photograph. They treat the variety across a weathered surface as samples of different degrees of the same process, and order them into a path through appearance that then drives weathering on new objects (abstract and patent; secondary). Bellini, Kleiman and Cohen-Or (2016) estimate the degree of weathering across a single texture from how prevalent its patches are, and make past and future versions (abstract; secondary).

### Context decides the pattern

Lu and colleagues, "Context-Aware Textures" (2007, with Dorsey and Rushmeier), ran controlled ageing experiments on real objects, measured the shape, and related each texture's change to geometric context. Their table of effects and the context each depends on:

| Effect | Context it follows |
| --- | --- |
| Copper patina | occlusion |
| Rust | occlusion, curvature, direction to the source |
| Paint cracking | coating thickness |
| Paste cracking and peeling | curvature, principal direction |
| Dirt accumulation | occlusion, direction of the source (gravity) |
| Mould | occlusion |
| Drying (Lu et al. 2005) | accessibility, distance to the wet/dry boundary |

They also showed cascades: rust that follows paint cracking, rust after peeling. One process opens the way for the next.

The survey by Mérillou and Ghazanfarpour (2008) classifies ageing phenomena by material and cause; we could not open it (its archive blocked automated reading), so its classification is not used here.

### How far games use this

Games took the context and left the cause and the clock. Substance Painter's dirt generator is built on baked occlusion, curvature, position and world-space normals, with a level, a contrast and a seed (Adobe documentation). Its edge-wear generators run on curvature. That is Miller's accessibility and Wong's tendencies, with no source, no path and no time. It is fast and controllable, and it gives every crevice the same dirt and every edge the same chip, which is why it reads as the generic weathered look. Naughty Dog paints its wetness by hand and shades moss from close observation, and both look right. We found no shipped game that runs flow or transport through time over a whole town (unverified: we may have missed one).

### What our water, wear and growth systems can learn

- Water both washes and stains. `water.py` bakes where water lands, runs, drips and pools. It should also bake flow rate (washing) and the end of flow (deposit), and `Water.hlsl` should draw clean where washed and grime where water slows, soaks in or stops.
- Carriers. Water carries what it dissolves: rust, copper, lime, tar, soil. A stain's colour and timing come from the source material upstream.
- One curve per process per material, a rate per point. The rate comes from the fields (water, sky, salt, feet); the start from the reset year. Our shaders already read years since reset; they should read a rate as well.
- Interactions. Moss suppresses splash; rust roughens and holds more dirt; peeling exposes what rusts. A layer reads the layers it depends on.
- Context as input, never as cause. Occlusion, curvature, coating thickness and direction to each source decide where a cause acts; they never stand in for the cause.

## 3. Film and stage

Production designers make places look lived in by building their past into them, and they talk about it as history: who patched what, and why.

- *Blade Runner* (1982). Ridley Scott imagined owners bolting new services onto the faces of old buildings because rebuilding cost too much: retrofitting. Syd Mead drew pipes, ducts and signs over photographs of the Warner Bros. backlot's New York Street, for a look of accretion: a panel refitted here, a bigger unit clamped on there because the old one failed. Deckard's flat was patched and taped rather than rebuilt (American Cinematographer, 1982). History reads as layers of fixes, each from a cause.
- *Star Wars* (1977). Roger Christian, the set decorator, told George Lucas he saw the future as a battered old car, repaired again and again, that keeps running (Star Wars Insider; secondary). He dressed sets with aircraft scrap because there was no money for anything else (Den of Geek).
- *Stalker* (1979). The Zone had to look as if no one had ever walked there; when dandelions bloomed in a prepared shot, the art department picked them without leaving prints or flattened grass (Sabzian, unsourced there; secondary). Absence of human traces is itself a claim, and it had to be true to the eye.
- *Children of Men* (2006). A critic noted worn-out technology and the lack of any new artwork: a world that stopped renewing shows it in how old its newest things are (Alternate Ending; secondary).
- Period work. Bob Shaw layered frames, wallpaper and fabrics in *The Gilded Age* so a house read as occupied for about two decades; another designer aimed for faded opulence and aged beauty without decay (Variety; Architectural Digest; secondary).

The scenic painter's craft is gravity and layers. Donna Wymore's film method stands the flat upright, base-coats it and sprays a thin raw-umber glaze along the top edge. Water sprayed into the glaze at once makes it run down; more water smooths snaky runs and sets the strength. What you don't like is brushed out while wet, and each pass dries fully (lighter than it looks wet) before the next colour (Painter's Journal, 2006, via Upstage Review). On Arizona Theatre Company's *Fences* set, umber washes from rags and sprayers built dirt, water marks and rust stains. The mortar was dirtied so it would not stand out against the grimy bricks, and the designer then marked where more was needed. Faded paint was dragged with a block of wood in the direction of the original strokes (Rosco Spectrum, 2016).

| Rule of thumb | Where it comes from | For us |
| --- | --- | --- |
| Let gravity draw the streak | scenic sprayers | streaks from the water layer, never painted on |
| Dirty the joints so they don't pop | Fences | joints carry the grime of their wall |
| Repairs as accretion, each with a reason | Blade Runner | the upkeep runner's patchwork |
| Layer occupancy to read decades | The Gilded Age | the stuff layer by household and decade |
| Absence must also be true | Stalker | no traces where no feet go |
| The age of the newest things tells the era | Children of Men | a bust decade has no new parts |

Gap: the standard scenic text (Crabtree and Beudert, *Scenic Art for the Theatre*, chapter on ageing) was behind a paywall; we have the practice from articles, not the book.

## 4. Scale models and dioramas

Modellers weather in layers, and the best of them order the layers by the vehicle's own history. Shadows and faded paint go first, then long-term wear and old dust, then recent effects such as rust and fuel spills, and mud, snow and fresh dust last (an Armorama article; secondary). Another thread on the same forum says the story you want to tell should set the order, not a fixed recipe (secondary). A common sequence starts with pin washes round bolts and seams, then filters (thin glazes that unify or shift the paint) and chipping where crews and tools touch. Streaking follows where fluids would collect or run, and pigments (dust, mud, soot) go on running gear and lower hulls last (Scale Model Shop guide; secondary). Rain marks are fine matt streaks of grit washed down vertical faces.

Their rules of restraint are explicit. From notes on a Mig Jiménez workshop: if you can see the technique, it is overdone; blend the effects into one coherent finish (secondary). From a guide: applying every effect at full strength leaves the eye nowhere to rest; halve the contrast when in doubt and look again a day later, since removing weathering is harder than adding it (secondary). Random streaks across flat surfaces look forced.

Scale changes what reads. The smaller the scale, the more the weathering must be compressed: chips smaller, rust lighter; heavy rust on a 1/72 model looks oversized, and fine streaking that works on 1/35 disappears smaller (secondary). This is our far tiers: at the city camera a mark merges into the thing's tone.

Railway modellers bring era and upkeep. Several argue that many layouts are over-weathered for their period. A 1900 building on a 1920s layout looks like it is falling apart, when it would be twenty years old and kept; prosperous decades built new and kept buildings well; old downtown buildings get repainted (Model Railroad Hobbyist forum). Others use weathering to show whether a house is alive and well, and keep the prosperous ones subtle. Buildings near the tracks collect soot, darker under awnings. And if you think it is over-weathered, it probably is (Zealot Models forum). Those who weather well gather prototype photos and work out what caused each discolouration (exhaust, splashed dirt, grime) before touching a brush (Trains.com forum; secondary).

Why it reads at small scale: few marks, each from a cause, all in one consistent finish, sized to the viewing distance. That is our "true up close, painted from afar" by another route.

| Diorama step | What it stands for | Our layer |
| --- | --- | --- |
| Base coat, factory colour | the thing as made | pigment and grain; tooling |
| Filters | sun fade, overall exposure | coatings fade; light |
| Pin washes | dirt in the recesses | occlusion as a context of dirt, not its cause |
| Chipping | wear at contact | wear: hands, boots, tools |
| Streaking, rain marks | water carrying dirt and rust down | stains from the water layer |
| Pigments, dust | ground thrown up, settled dust | splash band; airborne deposit |
| Fresh mud, wet effects | today's weather | weather |

## 5. Painters of places

Ruskin wrote the most useful line on decorative age in 1849. He held that a building's greatest glory is its age, "that golden stain of time" (*The Seven Lamps of Architecture*, The Lamp of Memory). He then split the picturesque in two. The lower kind is sought in ruin and decay for their own sake, and it extinguishes the character of the architecture: "the artist who looks to the stem of the ivy instead of the shaft of the pillar". The nobler kind keeps the building's own character and lets the stains and wear be an exponent of its age. He added that styles drawn in points of shade gain richness as they wear, while styles that depend on purity of line need hard materials. Weathering should follow the form it sits on.

- Vilhelm Hammershøi painted his flat at Strandgade 30 again and again: white woodwork, grey walls, few things, a worn step, rooms he admired for being a little worn at the edges (Apollo; Studio International; secondary). He said in 1907 that he chose a motif for its lines, its architectural stance, before light and colour (secondary). He often finished with a thin grey veil. Age reads because almost nothing else competes with it.
- Edward Hopper wrote in a note of 1946 that all he wanted was to paint sunlight on the side of a house (Lloyd Goodrich papers; secondary). *Early Sunday Morning* (1930) is a row of plain shopfronts; its history is carried by the planes in raking light and a few signs.
- Andrew Wyeth made about 300 works of the Olson house and its family over three decades, from 1939 to after 1967, in tempera and drybrush that render weathered wood and dry grass precisely (Farnsworth Art Museum; Bangor Daily News; secondary). One house returned to for thirty years is our years sheet.
- Simon Stålenhag starts from his own photographs and repaints everything in brushstrokes with no photo textures (CNN). Reviewers note his decay, abandonment and old technology kludged onto new (NPR; secondary).
- Harald Sohlberg painted Røros's mining town from 1902, its street drawn with documentary care in the foreground and the distance soft; the paintings helped prompt the town's restoration (Lex.dk; Bergbaumuseum; secondary).

What painters teach about history in things:

- Restraint makes history readable. One worn step in a calm room tells more than a room covered in wear.
- History lives in the light. Raking light shows relief, wear and repair; flat light hides them (our reading). Hopper built his fronts from plain planes in raking sun.
- The form holds; the marks serve it (Ruskin).
- Return to the same place. Hammershøi's rooms, Wyeth's house, Pentiment's town: change is seen against what stays.

## 6. Real buildings and streets

### Water on facades

Rain washes and stains at once. In polluted towns, rain dissolves the gypsum crust on limestone where it falls, so washed faces stay pale; under cornices, sills and in narrow streets, sheltered from the rain, the crust grows black with soot (USGS; studies following Camuffo, Del Monte and Sabbioni 1983; secondary). The black and white pattern of an old city facade is a map of where rain reaches. Sills shed water off their ends and streak the wall below unless a drip groove breaks the path; a sill that does not project, or has no groove, streaks (building practice; secondary). The foot of a wall takes rain splash, run-off and rising damp, and German plinth practice treats roughly the bottom 30 cm as the splash zone (HASIT, a render maker, via Heinze; secondary). Mostafavi and Leatherbarrow's *On Weathering* (1993) argues that weathering continues the building process, and that its details (drips, copings, sills) decide how a building ages (publisher's summary; we did not read the book).

### Air: soot, dust and salt

Dirt arrives from sources and has a direction: traffic at street level, chimney smoke on the faces downwind, salt from the sea side. Dorsey's paper notes a building that curved away from the street and carried less traffic dirt. Railway modellers soot the buildings near the tracks and darken them under awnings. For our town: wood and coal stoves, then oil from the 1960s, then electric heat (unverified for Stavanger's dates); cannery stacks on the quays; boats' exhaust at the quays; traffic grime from the 1960s.

### Life on surfaces

Algae grow most on north faces and moulds on south faces of rendered walls, and both show most in spring and autumn (Lund University study; secondary). Night-time radiation to a clear sky cools a facade below the air and wets it with dew, which is why insulated, thin-skinned walls go green (Fraunhofer; secondary). More than 200 species of algae, fungi, mosses and lichens colonise facade coatings in succession (Hofbauer; secondary).

### Sun, paint and timber

Paint on wooden houses fails first on the walls most exposed to sun and rain, usually south and west, and on the ends and edges of boards; moisture is the most common cause of early failure (Purdue Extension NCR 133; secondary). Unpainted wood erodes from about 0.03 to 0.1 mm a year on a vertical south face, faster as the face tilts towards horizontal (Williams and colleagues, Forest Products Laboratory; secondary). Norway's Institute for Cultural Heritage Research (NIKU) dates finishes by sampling paint layers in cross-section, from the first colour scheme up; on exteriors a new coat goes on about every decade on average, often changing the colour. One forum owner paints the whole house every seven to ten years and the weather wall every two to four (byggebolig.no; secondary, anecdotal). So the most weathered wall is often the most recently painted one, which a reader could misread.

Old painted lettering on walls survives for a century because its lead paint bonds to masonry (ghost signs; secondary), and shows through where later coats are thin or worn (unverified).

### Metal

Rust stains come from run-off from flashings, gutters, statues and fasteners; conservators find and stop the source before cleaning anything (US General Services Administration procedure; secondary). Iron fixed in stone rusts, swells and splits it.

### Touch

Where people touch, patina goes. Dublin's Molly Malone statue has been rubbed from dark bronze to gold where people touch it; Lincoln's nose at his tomb in Springfield is rubbed for luck (secondary). On paint the same contact first darkens (grease and grime at hand height round handles, switches and door frames) and then wears through to the coat below (cleaning guides; secondary).

### Inside

Dust and soot settle on cooler strips of ceilings and walls over joists and studs, drawing the framing in grey lines ("thermal tracking"; InspectAPedia; secondary). A picture taken down leaves a clean rectangle in faded wallpaper (unverified, common observation).

### How historians read a building

Buildings archaeologists read phases from evidence (Historic England's guide, as summarised by its blog; secondary). Brick or stone of a different colour, size or pattern marks a different build. A straight vertical joint marks where an addition or a blocking meets older work; a ragged joint, a section rebuilt. They also read peg holes and empty mortices in timber, blocked openings, changes in wall thickness and alignment, and fittings that can be dated. They order events by superposition and by what cuts what, in a Harris matrix: later over earlier, and a cut breaks the links between the layers it passes through (secondary). In a standing building the oldest parts are those that resisted time.

Two conservation texts set the ethic for a repair. William Morris's SPAB manifesto (1877) asked owners to stave off decay by daily care and put protection in place of restoration, and noted that each old change, "whatever history it destroyed, left history in the gap". The Venice Charter (1964), article 12, asks that replacements fit the whole but stay distinguishable from the original, so restoration does not falsify the evidence.

### Photographers

Bernd and Hilla Becher photographed water towers, winding towers and houses of one type each from the same frontal view in overcast light, and showed them in grids, so likeness and difference within a type stand out (MoMA; Fraenkel; secondary). Camilo José Vergara photographed the same buildings in Harlem, Detroit and elsewhere from the same spot for decades; Stewart Brand called it a perfect illustration of *How Buildings Learn* (Kottke; secondary). Both are review methods we already lean towards: grey light, fixed views, side by side.

### Where marks go on a house in this town

| Zone | Cause | Mark | Layer |
| --- | --- | --- | --- |
| Foot of wall, about 30 cm | rain splash, soil, damp | dirt band, green film, paint lifting, rot at the bottom boards | stains (splash); growth; coatings |
| Under sill ends and below projections | run-off concentrated at ends | streaks, grime at the end of the wash | stains (water) |
| Sheltered under eaves and cornices | no rain wash, deposit | dark band of soot and dust; unweathered paint; brown timber where exposed timber went silver | stains (deposit); coatings |
| Weather wall (south and west here; unverified for the town's winds) | sun and driving rain | faded, chalked or peeling paint, or the freshest coat | coatings |
| North wall, shaded | damp and dew | algae film, moss at the foot | growth |
| Under iron and copper | carried rust and verdigris | orange or green runs below the source | stains (carried) |
| Hand height at doors and gates | touch | grime, then paint worn through; polished latch | wear |
| Door and step | feet | hollow, polish, no growth on the line | wear |
| Downwind of chimneys and stacks | smoke | soot on the lee faces | stains (deposit) |

## 7. What makes history readable and true

### Principles

1. Every mark has a source, a path and an age. Draw nothing that cannot answer where it came from, how it got there and when. Caused marks cluster where their causes cluster; uncaused marks spread evenly and read as speckle.
2. Water washes and stains. Show the clean as well as the dirty. A washed face beside a sheltered one is the strongest single read of exposure.
3. One curve per process, a rate per point. A layer's state is the material's curve for that process, read at the point's own rate since its own reset. The pattern comes from the rates; continuity comes from the curve.
4. Order by time. Newer over older; a work cuts what was there before it. Readers can follow superposition, and nothing in the image may break it.
5. The form comes first. Weathering shows the thing's age without hiding what the thing is.
6. Restraint scaled to distance. Few marks, each meaning something, merged into tone with distance. If the technique shows, it is overdone.
7. Weather to the era and the keeper. A kept house in a good decade looks kept. Over-weathering lies about age and care.
8. Parts date; surfaces age. An installed part from its decade dates a front; patina only says old or new.
9. Things recur with their people. The same chair, sign or boat in a later home or year ties a person and a place across time (criterion 2).
10. Absence is evidence. Where nothing walks, nothing wears; where nothing is renewed, the newest thing is old.
11. Let things be missed. Evidence placed by causes, never spotlighted.
12. Repairs stay distinguishable. A repair reads as a repair; the evidence is never falsified.

### What makes it noise or a lie

| Fault | Why it misleads | Where seen |
| --- | --- | --- |
| Dirt in every crevice, wear on every edge | context without cause; claims nothing, reads as a look | curvature and occlusion generators |
| A seeded mark with a shape | readers infer a cause the facts never had | sandstorm study; Unpacking's warning |
| Over-weathering | lies about age and upkeep | railway layouts; modellers |
| An anomaly with no event | promises a story that isn't there | the pocket watch |
| A tableau | a moment told loudly and repeated as formula | posed skeletons |
| Decay as mood | turns care into a verdict on people | the engine's human test |
| Detail that buries form | the lower picturesque | Ruskin; Naughty Dog's fluff |
| A mark that crosses a newer repair | breaks superposition; dates the repair wrong | (our own check) |

### Age value and historical value

Alois Riegl (1903) separated a monument's age value, read by anyone at once from its visible signs of age, from its historical value, which belongs to a specific dated document and needs knowledge to read (via Holtorf 2017; secondary). Holtorf adds that the sense of pastness also comes from context and from how well a thing matches what people expect the past to look like, so copies can feel old. Both halves map onto our history budget:

| View | What reads | Riegl |
| --- | --- | --- |
| City camera | one history per thing: kept or let go, old or new, a gap, a different roof | age value |
| 12 m | coats by decade, window types per floor, a rebuilt panel | age value turning to historical |
| Street stop | a ghost sign, a dated part, a trench, a patch's material | historical value |
| Eye level | the cement's sand, a reset step's torn lichen, the worn door edge | historical value, clustered |

Holtorf's warning is ours too: pastness can be produced without a past. Our generators must never make a thing look older, newer or more neglected than its facts.

## 8. Layers: order and cause, mapped onto our systems

### The layer law

For each history layer on each part, the state at year `t` is the material's curve for that process, read at `rate(x) × (t − reset(x))`, after Gu's factorisation. The curve is the material's (how cement greys, how paint chalks, how lichen spreads). The rate is a bake from the fields at that point (water, sky, sun dose, wind and salt, feet, hands, deposit). The reset year comes from the record (made, or the last work that touched that point). Each layer reads only the layers it depends on (moss suppresses splash; paint failure opens the way to rust and rot).

This is a small change to what we have. The shaders already take years since reset; they need a per-point rate and a curve per material and process (a small lookup).

### Time order over type order

Our stack (`docs/foundations.md`) is ordered by type: pigment, tooling, wear, stains, growth, damage and repair, weather. Drawing in that order is fine as long as each mark knows its year. Two rules keep it true:

1. A repair is its own surface with its own stack from its year (as `docs/upkeep.md` already says). Stains, growth and wear on it start at its year.
2. Marks from before a work are cut at the work's edge; marks after it cross it. A rust run under a sign bracket taken down in 1974 fades from 1974 and vanishes under the 1988 coat of paint, but stays on the stone plinth below, which no coat reached. A streak from the 1980s runs across a cement patch of 1971. The cause view can show this, and a check can enforce it.

### Dirt up and dirt down

Scenic painters, modellers and building pathologists agree on two directions. Dirt comes down with water from above (run-off, streaks, rain marks, rust and copper runs) and stops where the water stops. Dirt comes up from the ground (splash, mud, soil, the damp foot) and fades within about 30 cm, higher above ledges and kerbs. Between them, sheltered zones collect what the air brings (soot, dust) and are not washed. Our water layer has the down and part of the up; it has no deposit.

### Causes, fields and layers

| Cause | Field (living fabric) | Bake (generator side) | Layer | Reads at |
| --- | --- | --- | --- | --- |
| Rain and run-off | water | land, run, drip, pool, flow rate, end of flow | stains; weather; growth | 12 m (washed against sheltered); street stop |
| Splash | water | distance above ground and ledges | stains (splash) | street stop |
| Smoke, traffic, dust | deposit (missing) | exposure to each source; rain shelter | stains (deposit) | 12 m |
| Salt and wind | wind and salt | facing the sea; height | stains; coatings; rates | 12 m |
| Sun | sky (and sun dose, missing) | hours of sun per face | coatings fade; timber silver; growth | 12 m |
| Feet | feet | walking line per part | wear | street stop |
| Hands and objects | uses (missing as a bake) | hand height at doors, gates, rails; lean and scrape spots | wear | eye level |
| Iron, copper, lime upstream | water with carriers (missing) | trace from source down the flow | stains (carried) | street stop |
| Care | care | patch and repaint rates | upkeep; coatings | 12 m |
| Time | the record | reset year per point | all | all |

## 9. What our systems are missing

| Missing | What it is | Where it belongs | Evidence |
| --- | --- | --- | --- |
| Airborne deposit and washing | soot, dust, salt from sources by era; dark where sheltered, clean where washed | a deposit field in the living fabric; a wash and deposit bake in `water.py`; the stains layer | Dorsey 1996; Camuffo; modellers' soot |
| Carried stains | rust, verdigris, lime white, tar, soil carried down the flow from a source material, across parts | `water.py` carriers; stains layer | Dorsey 1996 (differential flow); γ-ton stain-bleeding; GSA |
| The splash band | dirt, film and damp in the bottom 30 cm and above ledges | a term of its own in the water bake | Dorsey 1996; HASIT |
| End of flow | the deposit line where run-off soaks in or stops | water bake | Dorsey 1996 (partial flow) |
| Coat stack | coats by keeper and decade, failure by context (board ends, bottom boards, sills, weather wall), chalking, wear-through at handles, ghost signs | the coatings system (planned) | NIKU; Purdue; Lu 2007; ghost signs |
| Contact wear beyond feet | hands at doors, gates and rails; shoulders and bags in narrow lanes; bikes leaning; bins scraping; per material (paint greases then wears through, brass polishes, stone polishes, timber smooths) | `wear.py` | statues; cleaning guides; Hsu and Wong (scraping) |
| Sun dose | sun hours per face for fading, chalking, timber silvering, algae and mould by aspect | a bake beside the sky map | Purdue; FPL; Lund |
| Per-point rates | each layer's rate from the fields, not only years since reset | every history layer | Gu 2006 |
| Superposition check | newer over older, works cut older marks | the cause view and a validator | Harris; modellers; Morris |
| Seasonal visibility | algae and moss brighter and greener in spring and autumn | growth and weather | Lund |
| Interior traces | dust on up-facing surfaces away from use; thermal tracking; soot over stoves; a pale rectangle where a picture hung | interiors (plan step 8) | Hsu and Wong; InspectAPedia |

## 10. A cold reader's test for criterion 1

Criterion 1 asks that a viewer can say which parts are old, changed or neglected, and is right. Absolute dating from surfaces is hard even on real houses: seven students assigning decades (1960s to 2010s) to 470 photos of houses were right 36 per cent of the time (Zeppelzauer and colleagues, 2018). The authors note that telling an older building from a newer one is relatively easy. So the test asks for relative and categorical judgements first, and dates only where a dated part carries them. Readers also differ in taste. In a survey of 864 people in the US, respondents disliked decayed earth, concrete and rusting iron and were neutral about aged brick; the widest split was between preservation professionals and everyone else (Wells 2020; secondary). Cold readers should come from the public.

### The material

Frames from the judging views (city camera, 12 m, street stop, eye level), in grey light first, then in the three lights, and the years strip of the same view (1935, 1960, 1989, 2020). Every frame comes with its answer key from the record: the histories on show (the history budget), each with its cause, year and parts, exported by the cause view.

### The readers

People who have not seen the town or its docs, outside the art team. Five to eight per round while building (small panels can rank aged materials reliably; De Korte and colleagues used five observers in 2022, secondary), and twenty or more for a gate.

### The tasks

1. *Mark the parts.* On each frame, outline what is old, what was changed later, and what is neglected. Scored per part against the key: right, wrong, missed.
2. *Order.* For pairs of parts (two steps, two panels of a wall, two fronts), which is older? Scored against the record.
3. *What happened here?* Free text, as in the sandstorm study. Each claim is coded against the key: a fact; a fair interpretation of facts; a claim about seeded texture (false history); or a contradiction of the facts.
4. *Confidence.* Each answer gets a confidence. Confident claims about texture are the most serious failure.
5. *Across years.* On the strip, what changed between each pair of years, and why.

### Controls

- The same frames with every history layer off: what readers invent from forms and texture alone (the apophenia baseline).
- The same frames with the facts shuffled between things: if readers score as well, they are not reading our facts.
- One true anomaly with its event (a single out-of-era part), to see whether it pulls the eye as the pocket watch did, and whether the story readers build matches the record.
- The page: the same facts as text (criterion 4).

### Pass, provisionally

Our numbers, to be set by the first rounds. At the street stop and 12 m, at least four in five of the parts marked old, changed or neglected are right, and at least two in three of the histories in the budget are found. Pairs ordered right at least four times in five where the record differs by twenty years or more. At most one false history claim per frame on average, and none held with high confidence. On the strip, readers say the place is busier, poorer, kept or let go in the right direction between every pair of years.

### What failures mean

A false claim on texture means a seeded mark has a shape: fix the seed's scale. A missed history means the mark is too weak for its view or hidden in shade: move it into the light or into the budget's shape. A contradiction means a rule draws more than its facts (the `derived` rule in `docs/living-fabric.md`): tighten the rule. Results go in `docs/experiments.md` against the frames.

## What we should do

Ranked by how much each moves criterion 1, cheapest first where equal.

1. **Write the layer law into the shared layers.** Every history layer takes a per-point rate baked from the fields and a material curve for its process, beside the years since reset it already reads. Start with stone's stains and growth on the gully; judge it on the gully's years sheet (smooth change, no jumps except at works).
2. **Wash and deposit in the water bake.** `water.py` adds flow rate (washing), the end of flow (deposit) and rain shelter; `Water.hlsl` draws clean where washed and grime where flow ends or rain cannot reach. Judged on the corner's wall and plinths in drizzle and low sun: the washed and sheltered pattern reads from 12 m.
3. **A deposit field.** Add smoke, dust and salt to the living fabric's fields, with sources by era (stoves by heating era, the cannery stack 1898 to 1982, the quay's boats, traffic from the 1960s, the sea). Its strength is a fact of the setting's timeline; where it lands is the bake.
4. **Carried stains.** Sources (iron fixings, rails, copper and zinc flashings, concrete and lime, tarred roofs, soil) write a carrier into the water bake that runs down the flow path across part boundaries. A removed fixing keeps its stain, fading from its removal year. First case: the gully's handrail post and the lantern bracket.
5. **The splash band** as its own term (about 30 cm, and above ledges and kerbs), suppressed by moss and by paving that does not splash (after the γ-ton result).
6. **The superposition check.** The cause view gets a mode that shows each mark's year; a validator fails any mark older than a work that it crosses inside the work's scope. Run it on every years sheet.
7. **Design the coatings system with the houses** (plan step 2). Coats come by keeper and decade, about one a decade when kept. Failure follows context: board ends, bottom boards, sills, the weather wall, coating thickness. Chalking follows sun dose; wear goes through at handles; ghost signs show through thin later coats. Judge house A's front at 12 m and the street stop across its four states.
8. **Contact wear beyond feet.** `wear.py` takes hand zones (door handle side, gate latch, rail tops at hand height), shoulder rub in lanes under about 1.5 m wide (unverified threshold), and lean and scrape spots from habits, each answered per material.
9. **A sun-dose bake** beside the sky map, for fading, chalking, timber silvering under open sky against brown under eaves, and algae north against mould south.
10. **Run the cold reader test** on the gully's years sheet first, then the corner, with the controls above, and record it in `docs/experiments.md`.
11. **Make dating come from parts.** Each house kind and each street thing gets at least one part per era that dates it (window, plate, lamp, sign, kerb). Surfaces then only need to say old or new, kept or let go.
12. **Review in typology and years sheets.** Same view, same grey light, instances side by side (the Bechers) and years side by side (Vergara, Wyeth). Add one review question to every history review: can you see the technique?

## Gaps

- Scenic art. No primary text on scenic ageing rules was read; Crabtree and Beudert's chapter was paywalled. The practice here comes from articles.
- Diorama order. No primary source from Mig Jiménez or another master on the order of layers; forum and shop guides only.
- The 2008 survey. Mérillou and Ghazanfarpour's survey could not be opened, so its classification of phenomena is missing.
- On Weathering. Mostafavi and Leatherbarrow's book was not read; only its summary.
- Our town's air. No source on soot on Norwegian timber towns, or on when Stavanger's houses moved from wood and coal to oil and electric heat. The deposit field's eras are unverified.
- Paint here. Paint failure by orientation comes from North American extension guides and a forum; we found no Byggforsk numbers for repaint intervals by aspect.
- Splash height. The 30 cm comes from a German render maker's guidance, not from measurement.
- Thin game sources. Riegl is quoted second-hand. Red Dead Redemption 2, Elden Ring, Shadow of the Colossus, Outer Wilds and Kentucky Route Zero are sourced from wikis and reviews. Appearance manifolds (2006) and Bellini (2016) were read as abstracts only.
- Perception. We found little on which cues people use to judge a material's age; De Korte's thesis (2022) is the next read.

## Sources

Games: [Smith and Worch, What Happened Here?, GDC 2010](https://gdcvault.com/play/1012647/What-Happened-Here-Environmental) and [a copy of the slides](https://slidetodoc.com/level-design-workshop-what-happened-here-environmental-storytelling/) · [Harvey Smith, Nieman Storyboard 2011](https://niemanstoryboard.org/2011/01/14/harvey-smith-on-environmental-storytelling-and-embedding-narrative/) · [Smith Nicholls and Cook, That Darned Sandstorm, 2023](https://arxiv.org/abs/2304.08293) · [Unpacking at GDC 2022](https://www.gamedeveloper.com/gdc2022/gdc-2022-unpacking-a-narrative-through-1-000-household-items) · [How Naughty Dog created the world of The Last of Us Part II, 80.lv](https://80.lv/articles/how-naughty-dog-created-the-immersive-world-of-the-last-of-us-part-ii/) · [Art directing The Last of Us Part II, Cook and Becker](https://www.cookandbecker.com/en/article/250/art-directing-the-last-of-us-part-ii.html) · [Lemon Sky case study](https://www.lemonskystudios.com/case-studies-games/the-last-of-us-part-ii) · [Brinck and Maximov, The Technical Art of Uncharted 4, SIGGRAPH 2016](https://advances.realtimerendering.com/other/2016/naughty_dog/index.html) · [Prey's alternate history, Engadget](https://www.engadget.com/2017-06-05-prey-arkane-alternate-history-space-race.html) · [Gone Home's constraints, Game Developer](https://www.gamedeveloper.com/design/how-i-gone-home-i-s-design-constraints-lead-to-a-powerful-story) · [Edith Finch, Daily Star](https://images.thedailystar.net/node/1439071) · [The Art of Firewatch, Thumbsticks](https://www.thumbsticks.com/gdc-2015-the-art-of-firewatch) · [Revachol, Film Stories](https://filmstories.co.uk/?p=83234) · [Josh Sawyer on Pentiment, TheGamer](https://www.thegamer.com/interview-obsidian-josh-sawyer-pentiment/) · [Red Dead Online epilogue update, GTABase](https://www.gtabase.com/news/red-dead-redemption-2/red-dead-online-the-ultimate-concept-bundle-a-5-year-and-11-update-plan/update-10) · [Leyndell, Ashen Capital](https://eldenring.wiki.fextralife.com/Leyndell,+Ashen+Capital) · [Ueda's design by subtraction](https://blakecrosley.com/blog/design-philosophy-fumito-ueda) · [Outer Wilds, National Centre for Writing](https://nationalcentreforwriting.org.uk/writing-hub/the-writing-challenges-of-outer-wilds/) · [Outer Wilds, SFRA Review](https://sfrareview.org/2020/12/13/50-4-32/) · [Kentucky Route Zero, Kill Screen](https://www.killscreen.com/stop-everything-kentucky-route-zero-act-iv-right-now/) · [Environmental storytelling skeletons](https://knowyourmeme.com/memes/environmental-storytelling-skeletons) · [A garden of bodies, Giant Bomb](https://giantbomb.com/posts/guest-column-a-garden-of-bodies)

Graphics research: [Dorsey, Pedersen and Hanrahan, Flow and Changes in Appearance, 1996](https://graphics.stanford.edu/papers/flow) · [Dorsey et al., Modeling and Rendering of Weathered Stone, 1999](https://graphics.stanford.edu/~henrik/papers/sig99/) · [Chen et al., Visual Simulation of Weathering by γ-ton Tracing, 2005](https://faculty.cc.gatech.edu/~jarek/graphics/papers/15WeatheringChen.pdf) · [Gu et al., Time-Varying Surface Appearance, 2006](https://www.cs.columbia.edu/CAVE/publications/pdfs/Gu_TOG06.pdf) · [Wang et al., Appearance Manifolds, 2006](https://www.microsoft.com/en-us/research/?p=152023) · [Lu et al., Context-Aware Textures, 2007](https://graphics.cs.yale.edu/sites/default/files/p1-lu.pdf) · [Bellini, Kleiman and Cohen-Or, Time-varying weathering in texture space, 2016](https://history.siggraph.org/?p=102864) · [Mérillou and Ghazanfarpour, A survey of aging and weathering phenomena, 2008](https://hal.archives-ouvertes.fr/hal-00333283) · [Hsu and Wong, Simulating Dust Accumulation, 1995](https://webarchive.lib.cuhk.edu.hk/20210324161456mp_/http://www.cse.cuhk.edu.hk/~ttwong/papers/dust/dust.html) · [Substance 3D Painter dirt generator](https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/effects/generators/dirt)

Film and stage: [Blade Runner production design, American Cinematographer 1982](https://scrapsfromtheloft.com/movies/blade-runner-1982-production-design-and-photography-american-cinematographer/) · [Roger Christian, Den of Geek](https://www.denofgeek.com/movies/the-den-of-geek-interview-roger-christian) · [Stalker, Sabzian](https://sabzian.be/film/stalker) · [Children of Men, Alternate Ending](https://www.alternateending.com/2013/10/alfonso-cuaron-children-of-men-2006.html/amp) · [Bob Shaw on The Gilded Age, Variety](https://variety.com/2022/artisans/awards/production-designer-bob-shaw-layered-hbo-gilded-age-1235161527) · [Simple scenery aging, Hollywood style](https://www.upstagereview.org/post/simple-scenery-aging-hollywood-style) · [Distressing Fences, Rosco](https://spectrum.rosco.com/index.php/2016/08/distressing-fences)

Modelling: [Scale model weathering guide](https://www.scalemodelshop.co.uk/scale-model-weathering-guide-realism/) · [Mig Jiménez workshop notes](https://www.scalemodelshop.co.uk/?p=63066) · [Armorama on weathering order](https://archive.armorama.com/features/34-page=2.htm) · [Armorama forum on order](https://archive.armorama.com/forums/201970/index.htm) · [Over-weathered structures, Model Railroad Hobbyist](https://model-railroad-hobbyist.com/node/3975) · [How much weathering, Zealot Models](https://www.zealotmodels.com/threads/how-much-weathering.98416) · [Weathering advice, Trains.com forum](https://forum.trains.com/t/weathering-any-advice/238878)

Painters and critics: [Ruskin, The Seven Lamps of Architecture, 1849](https://www.gutenberg.org/ebooks/35898) · [Morris, SPAB manifesto, 1877](https://www.marxists.org/archive/morris/works/1877/spabman.htm) · [Hammershøi, Apollo](https://apollo-magazine.com/vilhelm-hammershoi-jacquemart-andre-paris/) · [Hammershøi, Studio International](https://studiointernational.com/index.php/hammershoi-the-eye-that-listens-review-museo-nacional-thyssen-bornemisza-madrid) · [Hopper's note, Wichita Art Museum](https://wam.org/our-collection/collection/sunlight-on-brownstones/) · [Wyeth and the Olson House, Farnsworth](https://www.farnsworthmuseum.org/about/fam-blog/the-olson-housebeyond-wyeths-brushstroke-exploring-a-maine-art-legacy/) · [Wyeth's Olson paintings, Bangor Daily News](https://www.bangordailynews.com/2011/07/28/living/andrew-wyeth’s-olson-house-paintings-return-to-maine/) · [Stålenhag, CNN](https://edition.cnn.com/style/article/simon-stalenhag-sci-fi-art) · [The Electric State, NPR](https://www.npr.org/2018/10/21/658921379/futuristic-dreams-turn-to-nightmare-in-electric-state) · [Sohlberg, Gate i Røros, Nasjonalmuseet](https://www.nasjonalmuseet.no/en/collection/object/NG.M.00883) · [Sohlberg, Lex.dk](https://lex.dk/Harald_Sohlberg) · [Sohlberg and Røros, Der Anschnitt 1984](https://www.bergbaumuseum.de/fileadmin/forschung/zeitschriften/der-anschnitt/1984/1984-01/anschnitt-1-1984-slotta-sohlberg.pdf) · [Holtorf, From age value to pastness, 2017](https://www.cambridge.org/core/journals/international-journal-of-cultural-property/article/abs/perceiving-the-past-from-age-value-to-pastness/F3A99D23A2DE1A7DF9C25E77112DFCE5)

Buildings: [Black crusts on limestone, USGS](https://pubs.usgs.gov/gip/acidrain/5.html) · [On Weathering, MIT Press](https://mitpressbookstore.mit.edu/book/9780262631440) · [Splash zone, HASIT via Heinze](https://www.heinze.de/produktserie/sockelabdichtungen-an-der-fassade/50014525/1/) · [Biological growth on rendered façades, Lund](https://www.lunduniversity.lu.se/lup/publication/03f68734-3706-438b-967d-41c4afdfc6f7) · [Algae on ETICS, Detail](https://inspiration.detail.de/en/article/research-and-practice-algae-growth-on-etics-a-problem-without-a-solution-1327) · [Purdue NCR 133, wood finishes](https://extension.purdue.edu/extmedia/ncr/NCR-133.html) · [Williams et al., erosion of wood](https://wfs.swst.org/index.php/wfs/article/view/884) · [NIKU, architectural paint research](https://www.niku.no/en/apr) · [Repainting intervals, byggebolig.no forum](https://www.byggebolig.no/eksterior-tak-ytterkledning-og-maling-(ute)/utfordring!-vedlikeholdskostnader-ved-tradisjonell-utvendig-kledning) · [Ghost signs](https://en.wikipedia.org/wiki/Ghost_sign) · [GSA, rust stains](https://gsa.gov/real-estate/historic-preservation/historic-preservation-policy-tools/preservation-tools-resources/technical-procedures/poulticing-rust-stains-from-limestone-and-marble) · [Statue rubbing](https://en.wikipedia.org/wiki/Statue_rubbing) · [Thermal tracking, InspectAPedia](https://inspectapedia.com/interiors/Thermal_Tracking_Lines.php) · [How to do buildings archaeology, Historic England](https://heritagecalling.com/2016/07/28/how-to-do-buildings-archaeology/) · [Harris matrix](https://en.wikipedia.org/wiki/Harris_matrix) · [Venice Charter, 1964](https://icomos.org/en/charters-and-texts/179-articles-en-francais/157-venice-charter-1964) · [The Bechers' Water Towers, MoMA](https://www.moma.org/collection/works/49624) · [Vergara, Tracking Time](https://also.kottke.org/16/04/tracking-time)

Perception: [Zeppelzauer et al., Automatic Prediction of Building Age from Photographs, 2018](https://arxiv.org/abs/1804.02205) · [De Korte, Logan and Bloj, Materials & Design, 2022](https://doaj.org/article/e74a00ae2f5f49cc8b6bc38d259cd869) · [Wells, the person-patina relationship, 2020](https://drum.lib.umd.edu/handle/1903/26348)
