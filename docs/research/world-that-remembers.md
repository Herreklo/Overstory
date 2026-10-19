# A world that remembers

Research synthesis for the Game Lab: how to build streets, buildings and places that are beautiful, change over time and show what happened in them. It draws on four research tracks (procedural architecture, simulated history in games, art direction, how real towns change) and turns them into rules for our system.

## The idea in one paragraph

A building is a diary of dated events, not a model. The engine writes the diary. A resolver turns the diary into a plan, and the plan is built from parts. Every part comes from the decade it was put in, every surface is a stack of coats that wear through to older ones, and every visible difference is a true fact about the world. The player reads a street the way they read a person.

## Twelve principles

**1. Visuals may elaborate facts, never contradict them or falsely claim history.** Players read meaning into anything. Will Wright saw SimCity players link events "that Will as the programmer knows are not actually related", and in a study of a generated ruined village, players read a softlock bug as an in-world sandstorm. So anything that reads as history (a later window, a ghost sign, a mismatched porch) maps to a diary entry, while stable seeded texture (a lean, a board width, a chair's angle) stays below the level of claiming a story. Five kinds of thing are on screen: canonical facts, visual interpretations of facts, non-semantic texture, perceived information (which may be wrong), and local scene state. *Sources: Wright via Hopkins; Smith Nicholls & Cook 2023; the external review of 19 October 2026.*

**2. Show a few things loudly and the rest quietly.** Raw simulation output has no story. James Ryan's work on curating simulated worlds shows that every successful emergent-narrative project selects what to show. Kate Compton's "10,000 bowls of oatmeal" warns that variety nobody can tell apart is worthless; a calm background makes the few characterful things stand out. Each event gets a weight (caused by a named person, inside this game's time window, unusual, linked to the player). Heavy events leave strong traces. The rest become ordinary, uniform ageing. *Sources: Ryan, Curating Simulated Storyworlds; Compton.*

**3. Anomalies pull the eye.** In the same village study, 51 of the 54 players who saw one out-of-place pocket watch examined it. Our anomalies are out-of-era parts: a 1970s door in an 1890s front, one modern shopfront in an old row. Each one is a real event, so following the anomaly leads to a real story. *Source: Smith Nicholls & Cook 2023.*

**4. Layers change at their own speed.** Stewart Brand (after Frank Duffy) splits a building into site, structure, skin, services, space plan and stuff. Structure lasts decades to centuries, skin changes every 15 to 25 years, the use of rooms every few years, and stuff (signs, curtains, bikes) monthly. A study of west-coast houses found them repainted about every 13 years. In our diary each layer has its own clock, which gives the time-lapse a natural rhythm: stuff flickers, skin shifts per decade, the bones stay. *Sources: Brand, How Buildings Learn; Skudeneshavn colour study.*

**5. Streets stay, buildings change, plots have a life.** M.R.G. Conzen showed that street lines and plots outlast the buildings on them. Each plot goes through a cycle: built, then the back fills up with sheds and workshops, a peak, decline, clearance, an empty "fallow" lot (a gravel car park in 1989), and rebuilding. Plots merge mostly in booms, for big commercial buildings. *Source: Conzen, Alnwick (1960).*

**6. Parts come from the decade they were installed.** A 1968 window replacement gets 1960s windows. The resolver picks a part in two steps, the way Wonka's "Instant Architecture" does: first filter by era (each part carries a year range), then choose with a seed tied to the event that installed it. One new event changes only the parts it owns; the rest of the building stays identical. *Source: Wonka et al. 2003.*

**7. Surfaces are stacks of coats.** Dorsey and Hanrahan model ageing as layers built by three operations: coat, erode, polish. A repaint is a coat, neglect erodes, a renovation strips back. Where wear goes through the top coat, the older layer shows: the previous colour, the grocer's lettering under the bar's sign, the outline of an old shopfront. Ghost signs and old colours then come for free, and they are always true. *Sources: Dorsey & Hanrahan 1996; Dorsey, Pedersen & Hanrahan 1996.*

**8. Additions fit the building, or visibly don't.** Christopher Alexander's idea of structure-preserving change: a good addition attaches to something that exists and strengthens it (a porch at the entrance, a dormer centred on the roof, an extension on the garden side, a shopfront in the street wall). Each era has a care score. Careful decades repeat the host's lines; careless decades (oversized replacement windows, cut-back eaves) break them. Streets then show which decades looked after them. *Source: Alexander, The Nature of Order.*

**9. Low-road and high-road buildings.** Brand's distinction. Warehouses, factories and sheds change use and openings cheaply and often: herring store, cannery, storage, offices, restaurant, flats. Villas and churches mostly repaint and repair, and are rarely altered. A tag on each building sets how its diary may grow. *Source: Brand.*

**10. Cheap old space breeds new life.** Jane Jacobs: "New ideas must use old buildings." Empty industrial buildings draw artists, rehearsal rooms and bars; new housing nearby pushes them out (London lost 35% of its music venues between 2007 and 2015, many after complaints from new neighbours). A local case: Stavanger's closed Tou brewery became an arts venue. This links buildings to play. Where a band can rehearse and perform depends on the city's building cycle. *Sources: Jacobs; Zukin, Loft Living; Agent of Change; Tou Scene.*

**11. Owners leave signatures.** In Caves of Qud each historic figure has "domains" that recur through every event of their life, so scattered traces read as one story. Our owners and families repeat a lettering style, a colour or a material across the buildings they touch. *Source: Grinblat & Bucklew 2017.*

**12. Booms and busts set the pace.** Each boom builds in its own style and each bust leaves empty shops and lots. Ålesund burned in 1904 and was rebuilt within three years in Art Nouveau. Streets become layers of their town's good and bad years, and districts get their character from history. *Sources: Conzen on fringe belts; Ålesund records.*

## The system

**The flow.** Engine facts → building diary → resolver → plan → parts in Unity. The same diary always gives the same plan.

**The resolver runs in five passes.**
1. *Massing.* Volumes from the diary: main body, wings, porch, veranda, bay window, dormers, lean-tos.
2. *Facade grid.* Each facade split into columns and storeys. Floor lines snap across volumes, so an addition from the same era lines up; an addition from a different era may break the line, which shows its date. Every cell is tested against the building's own volumes and against neighbouring plots, so a window never sits where a wing or a neighbour meets the wall. A window blocked by a later neighbour becomes a boarded cell dated to that neighbour. *Source: CGA shape grammar (Müller et al. 2006).*
3. *Parts.* Each cell gets a part: filtered by era, chosen by the installing event's seed.
4. *Decoration and sockets.* A separate pass after the structure, as in Townscaper. Sockets work like Minecraft's jigsaw blocks: each has a name, the part types it accepts, a pool per era and a priority. Sign bands take signs, eaves take gutters, sills take flower boxes, corners take downpipes. Sockets are anchored relative to facade edges, so they survive later changes. *Sources: Stålberg; Minecraft jigsaw.*
5. *Surfaces and wear.* The coat stack, wear masks (exposure, facing the weather, drip lines under sills and cornices, a dirt strip where walls meet the ground) and decals for stains, moss and ghost signs. The shader reads one number per layer: years since it was applied. *Sources: Lu et al. 2007; Ghost Recon Wildlands.*

**Roofs.** One roof over the combined footprint, built from a profile per edge (straight skeleton), so wings and porches join the main roof the way real roofs do. Gable ends are vertical profiles; dormers are small steps at anchors. The method can fail on awkward shapes, so every roof is validated and falls back to one roof per volume. *Source: Kelly & Wonka, Procedural Extrusions (2011).*

**Hard and soft rules.** Hard rules are structural; a failure stops the building and reports it. Soft rules shape taste (no two identical neighbouring fronts from the same era); a failure is quietly accepted. No global solver chooses parts: a whole-building solve would let one diary event change cells far away. *Sources: Bad North; Merrell on model synthesis.*

**Who decides what.** The engine decides facts: built, extended, repainted, converted, opened, closed, neglected, demolished, and why (who decided, and their reason). The plan decides how a fact looks. Unity builds walls and roofs at any size and places the detailed parts from Blender. Unity never decides a fact.

**Engine requests this adds.** A reason on every diary entry (who decided and why); plot life cycles; vacancy and rent; economic waves; the building's low-road or high-road character; footfall (who goes where, how often); street plans and how far each was carried out; weather that matters to the story.

## Between the buildings

The space between buildings carries as much history as the buildings, and it follows the same rules: it has a diary, its layers change at their own speed, and every trace is true.

**The street has a diary too.** Cobbles, then asphalt, then patches where trenches were dug for pipes and cables. Gas lamps, electric lamps, then orange sodium lights. Overhead wires to every facade, buried decades later. A tram line laid and pulled up, its rails sometimes still showing. Each change is a dated event on the street, and each leaves a trace.

**Trees are clocks.** A tree planted in 1960 is big in 1989 and huge in 2020. Planting is an event; size follows from age. Nothing tells the time of a street more gently.

**Use leaves wear.** Busy doorsteps are worn hollow. Paths across grass show where people walk. A bar has crates, bins and bikes outside; a venue has posters spreading over nearby walls and a queue line on the pavement; a closed factory has weeds in its yard. Footfall comes from the engine (who goes where), so the wear is true.

**Everything is connected.** Nothing stands alone, and every element has a reason and a connection:
- *Water:* roof to gutter, gutter to downpipe, downpipe to a drain in the street. Water runs downhill, so the low side of a street is wetter, and north-facing walls grow moss.
- *Heat:* chimneys exist because of stoves. Wood stoves, then oil heating (a tank in the garden), then electric. A chimney taken down is an event.
- *Power:* a lit sign needs a cable. Wires run from poles to facades until they are buried.
- *Access:* every door has a path to a street. A shop needs a street front; deliveries need somewhere to stop. When cars arrive, front gardens become driveways.
- *Ground:* hills need steps, ramps and retaining walls; quays need bollards, ladders and fenders. Salt spray weathers what faces the sea.
- *Neighbours:* one renovation makes the next more likely, so fresh paint spreads along a street. A tall new building shades its neighbours. Noise from a venue meets complaints from new housing.

## Built logic and planning phases

**Everything has to be buildable.** A second storey stands on a first. An overhang has brackets or a wall under it. An extension has a foundation. A window has a room behind it, a gutter leads somewhere, a door can be reached. These become the resolver's hard rules: a plan that breaks one is not built. Logic is what makes the world believable even when the shapes are pushed.

**Plans are a layer with phases, and only some of each plan gets built.** A street plan has its own diary. It starts with organic lanes, then straight streets laid out after fires, then modernist plans in the 1950s to 70s that widened roads and cleared old blocks, then conservation from the 1980s. Most plans were only partly carried out (Stavanger's own clearance plans were, around Olavskleivå and Klubbgata), so the city keeps their scars:
- a street widened at one end and stopping halfway;
- new buildings set back to a planned building line while their old neighbours stay on the old line, giving a stepped street front;
- a lone modern block where a larger scheme stalled;
- an empty lot that waited for a road that never came.

The plan is intention; the fabric is what happened; the gap between them is visible history. The engine (or the generated past) decides which plans were made and how far they got.

## Beyond buildings

**Place ladders.** A game climbs a ladder of places, and the climb is the story. For the band: bar, local venue, bigger hall, the pinnacle. Each rung escalates the same things in a fixed order: scale, light, crowd, materials, glamour. The street outside escalates too (a door in an alley, then queues and posters). Going back down to the first rung years later, changed, is the strongest moment, and the diary makes it cheap.

**Nature with a history.** Forests, paths and shores follow the same rules as streets: a diary of logging, paths worn in and grown over, a cabin built and abandoned, a clearing where something happened. A murder mystery in a forest needs exactly this, and its traces must be true because the player has to trust them.

## How the player reads it

- Fixed vantage points across years. The same street views recur across games set in different years, and within a game, so change is seen side by side. Pentiment shows one town in 1518, 1525 and 1543. *Source: Pentiment interviews; Smith & Worch 2010.*
- Archives and directories. Address books, business registers, photos, signs. People can misremember a building's past; the fabric never lies. *Sources: Talk of the Town; Bad News.*
- A journal of observed traces, pinned to a timeline, with deductions confirmed in groups. *Sources: Caves of Qud's journal; Return of the Obra Dinn.*
- Decisions write to buildings, through the engine. One choice sets a lasting building state and changes the neighbours' businesses. *Source: Stardew Valley's Community Center against JojaMart.*

## The look

Our style is found in look tests, not borrowed. What the research says about finding it:

- Atmosphere first. Sable called distance fog "really, really key" to readability and built its day cycle on it. SEASON wrote its own atmospheric perspective and height fog. In URP that means a full-screen pass of our own; the built-in fog has only three distance modes. *Sources: Sable GDC 2022; SEASON tech blog.*
- Shadow colour comes from the light, never from the object. SEASON started with a colour and a shadow tint per object, and had to drop it because every object needed re-editing whenever the time of day changed. *Source: SEASON tech blog.*
- One mood manager. One system blends sun, sky, fog, ambient light and grade between states. It carries our mood range (moody, cozy, alive, glam), and the engine's facts choose the mood: a struggling bar in drizzle, a family kitchen at blue hour, market day, a sold-out gig.
- Fake the bounce from the generator. Nothing can be baked because places change, and URP's real-time GI needs precomputation. The kit generator writes occlusion and a ground-bounce tint into each part at assembly, under a sky-and-ground ambient light. *Sources: Unity forums on Enlighten in URP; Tunic.*
- Forward+ rendering, for many warm window lights at blue hour and for Unity's custom lighting samples, which do not run in deferred mode.
- Detail where the history is. Firewatch gave story objects more detail; Kazuo Oga paints "the little things". Our plain walls stay calm and our junctions, signs and traces of change get the detail.
- Design the raised camera early. art of rally's team called the camera "the glue that held the entire experience together".
- No global painterly filter. A Kuwahara-style filter smears everything evenly and reads as a filter. Any brush or print texture goes on surfaces, fixed to the world so it does not swim.
- Borrow from outside games. SEASON took woodblock prints and mid-century posters; Pentiment took the period's prints. Candidates for us: Hopper's lit windows, Hammershøi's grey light, Sohlberg's blue night, Astrup's flat, wet west-coast colour, and the poster and sign culture of the decade a game is set in. These are inputs to test, not the identity.

**Generic-look traps.** A global oil-paint filter, even-width black outlines, pastel palettes with bloom and tilt-shift, shadows that are just darker colour, single-grey fog, noise textures everywhere, everything rounded, and no test in overcast light.

## The North Atlantic shelf

The first region's parts come from the North Atlantic timber harbour town: west-coast Norway, New England, the Maritimes, the Faroes. Painted clapboard, steep gables, white trim, quays with warehouses. Country-specific features are accents, not the identity. The first shelf, by era (from Stavanger's own guidance, generalised):

| Era | Years | Shape and roof | Windows | Ornament | Colours |
| --- | --- | --- | --- | --- | --- |
| Classical | to c.1870 | Small, 1½ storeys, symmetric, door central; gable with almost no overhang, big chimney at the ridge | Small panes, centre post | Panelled door, fanlight | White, sandstone, ochre, grey; green or ochre trim |
| Chalet | c.1865 to 1910 | Larger, high base; big decorated overhang | Tall cross-post windows in rich surrounds | Fretwork, spires, verandas and balconies | Ochre, sandstone, white; graining |
| Chalet-jugend | c.1905 to 1920 | Chalet with a winter garden; broken gable, then mansard | Cross-post with an arched pane | Tall chimney | Mostly white |
| Functionalist | c.1930 to 1950 | Asymmetric, flat or low roof | Corner windows, bands, no small panes | Entrance canopy | Red, ochre, then pale green, yellow, blue |
| Post-war | c.1945 to 1965 | Horizontal, low pitch | Big picture window beside small ones | Few | Colourful |
| 1970s | c.1965 to 1980 | Catalogue houses, terraces, low gable | Plain casements | None | Stained brown or red |
| 1980s | c.1980 to 1990 | Catalogue houses | Stick-on glazing bars | Little | Pastels |

**Later changes arrive in waves.** Old houses get them with rising probability in each period: windows replaced and decoration stripped (1950s to 70s), asbestos-cement plates (1950s to 60s), plain casements (1960s to 80s), concrete roof tiles (1970s to 90s), plastic cladding and stick-on bars (1980s), then restoration, sometimes in the wrong style. **Signs by era:** painted lettering and gable ads, black glass with gold leaf (c.1880 to 1915), neon (1930 to 50), oversized lit boxes (1950s to 70s).

## What this changes in LT1

- Four looks, not three: painted ramp, soft toon, graphic, plus plain URP Lit as a control, to show what stylisation adds.
- A fair comparison. All four share the same atmosphere, sky, palette and grade; only the lighting function and lines differ. Every frame also comes in greyscale and at one-eighth size, to test value and silhouette. A five-second camera move per look catches shimmer. Judged blind, labelled A to D. Drizzle counts most.
- The mood range is part of the question: can one look go from moody (drizzle) to cozy (blue hour) on the same street?
- The shape step uses the system: buildings resolved from diaries, and one building shown in three years.

## Sources

Procedural architecture: [Instant Architecture](https://www.cg.tuwien.ac.at/research/vr/instantarchitecture/instant_architecture.pdf) · [CGA shape grammar](https://course.ccs.neu.edu/cs5150f13/readings/muller_buildings.pdf) · [4D Cities](https://diglib.eg.org/handle/10.2312/CGF.v28i2pp481-492) · [Merrell, model synthesis vs WFC](https://paulmerrell.org/wp-content/uploads/2021/07/comparison.pdf) · [How Townscaper works](https://www.gamedeveloper.com/game-platforms/how-townscaper-works-a-story-four-games-in-the-making) · [Bad North WFC](https://80.lv/articles/using-wave-function-collapse-algorithm-for-dioramas) · [Minecraft jigsaw](https://minecraft.wiki/w/Jigsaw_block) · [Ghost Recon Wildlands](https://80.lv/articles/procedural-technology-in-ghost-recon-wildlands/) · [Shadows of Doubt interiors](https://colepowered.com/shadows-of-doubt-devblog-13-creating-procedural-interiors/) · [Procedural Extrusions](https://peterwonka.net/Publications/pdfs/2011.TOG.Kelly.ProceduralExtrusions.TechreportVersion.final.pdf) · [Flow and changes in appearance](https://graphics.stanford.edu/papers/flow) · [Metallic patinas](https://graphics.stanford.edu/papers/patina/) · [Context-aware textures](https://graphics.cs.yale.edu/sites/default/files/p1-lu.pdf) · [URP decals](https://docs-alpha.unity3d.com/Manual/urp/renderer-feature-decal.html)

Simulated history: [Talk of the Town](https://ojs.aaai.org/index.php/AIIDE/article/view/12825) · [Bad News](https://eis.ucsc.edu/papers/ryanEtAl_BadNewsCHI2016.pdf) · [Curating Simulated Storyworlds](https://escholarship.org/uc/item/1340j5h2) · [Caves of Qud history](https://pcgworkshop.com/archive/grinblat2017subverting.pdf) · [That Darned Sandstorm](https://arxiv.org/pdf/2304.08293) · [Pentiment interview](https://www.thegamer.com/interview-obsidian-josh-sawyer-pentiment/) · [Stardew Community Center](https://stardewvalleywiki.com/Community_Center) · [Gone Home](https://www.gamedeveloper.com/design/how-i-gone-home-i-s-design-constraints-lead-to-a-powerful-story) · [Will Wright via Don Hopkins](https://donhopkins.medium.com/designing-user-interfaces-to-simulation-games-bd7a9d81e62d) · [Environmental storytelling, GDC 2010](https://gdcvault.com/play/1012647/What-Happened-Here-Environmental) · [Compton, oatmeal](https://galaxykate0.tumblr.com/post/139774965871/so-you-want-to-build-a-generator)

Art direction: [Art of Firewatch](https://www.thumbsticks.com/gdc-2015-the-art-of-firewatch) · [Firewatch sky](https://blog.camposanto.com/post/112703721804/this-blog-post-is-an-in-detail-explanation-of-part) · [SEASON's illustrative look](https://www.unrealengine.com/en-US/tech-blog/creating-the-illustrative-look-of-season-using-unreal-engine) · [Sable readability](https://www.gamedeveloper.com/marketing/how-shedworks-refined-the-art-of-sable-in-pursuit-of-readability) · [Guilty Gear Xrd](https://www.ggxrd.com/Motomura_Junya_GuiltyGearXrd.pdf) · [Art of The Witness](https://www.artofluis.com/wp-content/uploads/2014/03/gdc2014_luisantonio_theartofthewitness.pdf) · [Pentiment's art](https://www.gamedeveloper.com/art/deep-dive-the-art-of-pentiment) · [art of rally camera](https://jalopnik.com/how-a-small-change-in-camera-angle-completely-transform-1849152549) · [Kazuo Oga](https://animationobsessive.substack.com/p/what-kazuo-oga-thinks-about-when) · [Sohlberg](https://www.nasjonalmuseet.no/en/collection/object/NG.M.01185) · [Astrup](https://theartstory.org/amp/artist/astrup-nikolai/) · [URP outlines](http://ameye.dev/notes/rendering-outlines/) · [URP volumetric light](https://github.com/CristianQiu/Unity-URP-Volumetric-Light)

Towns and buildings: [Shearing layers](https://en.wikipedia.org/wiki/Shearing_layers) · [Burgage cycle](https://journal.urbanform.org/index.php/jum/article/download/4064/3374/11705) · [The Nature of Order](https://en.wikipedia.org/wiki/The_Nature_of_Order) · [Jacobs on old buildings](https://misspreservation.com/2009/03/19/book-quotes-jane-jacobs-on-old-buildings/) · [Agent of Change](https://designingbuildings.co.uk/wiki/Agent_of_change) · [Tou Scene](https://snl.no/Tou_Scene) · [Stavanger wooden town](https://www.stavanger.kommune.no/siteassets/bolig-og-bygg/byantikvaren/trehusbykampanje-2021/trehusbyen-brosjyre-2021.pdf) · [Sjøhus plan](https://www.stavanger.kommune.no/siteassets/skjema-a-a/samfunnsutvikling/reguleringsplan/sjohusrekken-1993.pdf) · [Canning plan](https://www.Stavanger.kommune.no/siteassets/samfunnsutvikling/planer/temaplaner/bolig-og-bygg/hermetikkplan-2017---temaplan-for-hermetikkfabrikker-og-tilknyttede-virksomheter-i-stavanger.pdf) · [Skudeneshavn colours](https://www.karmoy.kommune.no/_f/p1/i30edc8cb-f585-4061-bf23-bfce08a9261f/historisk-fargekart-skudeneshavn.pdf) · [Signs in Oslo](https://www.oslo.kommune.no/get-file/111661/2399dbe645dc9e7e4c04839c1bd2ec1e2bf28fd70480dee35be501babf5e9871)
