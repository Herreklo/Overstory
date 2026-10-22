# LA: the light's range, on paper

1c's first stage, 22 October, Opus 5.5, Unity-free. It asks whether the light record that L1 will fix, and the terms of `OS_ShadeP`, give five regimes a place, so that later regimes add terms and keys instead of forcing a rebuild (`reviews/lt1/playable/outline.md`, 1b, LA). Its inputs: two craft studies, light under a canopy and many lamps at city scale (now `docs/research/lighting-and-colour.md` §10 to §12), and a read of today's light code (below, Today's code). A fresh Opus reviewer checked the draft adversarially; its eight findings are taken in. Nothing was built.

## In short

- **All five cases fit, if L1 fixes thirteen things now** (What L1 must hold). Everything else the cases need is an addition: a new block, a new map, a new key or a new term.
- **Five of the thirteen would force a rebuild if left out:**
  - art keys keyed by the sun's elevation and a continuous morning-to-evening weight, never the clock (else every season and latitude needs its own key set);
  - the sky held as a model's parameters with spherical harmonics derived from them, for the ambient, the dome and the reflections alike (else directional overcast, twilight, the night's cloud glow and the canopy's second sky each need a new term, and reflections show a second sky);
  - lamps held by reference and by circuit, never as a list or a tier (else a city's lamps swell every record, and tiers freeze to one camera);
  - nothing in the record that depends on place or camera: ground cover, cloud glow, canopy and town light live in maps (else one scalar must serve heath, setts, wood and snow in one frame);
  - caches stepped by absolute time, never "when the sun has moved" (else replay and time jumps give different frames).
- **Every term has a clock.** Each term falls into one of seven cost classes, from per pixel to offline, after the performance study's clocks. New regimes add mostly cached maps and per-frame colours. The per-pixel additions are one or two taps each (the fleck map, the seen ground, far lamp pools), plus, per lamp, a profile tap and nine multiply-adds for colour rendition, in a binned loop.
- **Today's code has three clocks, three lamp colours and two suns.** Nothing reads `schemas/world-state.schema.json`. The rig's date, its `clock` and `FabricDate` are separate. Sodium has three colours in three files. The clouds and beams get a different sun from the Light. The record replaces these; LA fixes none of them.
- **Two formats outside the record must hold too.** The page bake's sky seen must exclude tree crowns, with the canopy in a channel of its own; otherwise the season freezes into every face. And parts' light sockets need an emitter radius, a distribution and an upward ratio.

## The five cases

The weather in each is the case's assumption, not a claim about that day: in play the engine's weather decides. Sun positions are computed for Stavanger (58.97° N, 5.73° E) in local time; summer time ended on 24 September 1989. The cost classes are defined under The check.

**1. The Row at blue hour.** Friday 20 October 1989, 17:50 CET. The sun is 4.9° below the horizon at 258°, 33 minutes after sunset. Broken cloud, wet after showers. Street lamps switch on by photocell; shops are lit by their hours, rooms by their households. The sky is the key light, cool from above, with its bright side in the west. Lamps and windows are warm accents; the wet setts mirror both. *Needs:* a twilight sky model for the ambient, the dome and the reflections alike; lamps by circuit, their kinds draining colour; normalised lamp highlights on the wet stone; halos; exposure from about 10 lux; the blue-hour key by elevation. *Terms:* sky (a sun-step projection, then px), lamps (px per binned lamp), air (px), keys (frame). This is the corner's own regime. Today's rig types it all by hand, and has the lamps off at this hour.

**2. A birch wood at a summer noon.** Wednesday 21 June 1989, 13:40 CEST. The sun is 54.5° high in the south; fair, light breeze, dry; the birches in full leaf. Firewatch is the bar: pale trunks with a warm lit edge against a cool shaded side, layered air between rows of trunks, shafts, bold leaf clusters. The floor shows soft round flecks, not leaf shapes. A gap 12 m up throws a sun image about 14 by 17 cm, and a 5 cm leaf loses its sharp shadow about 5 m below it. A measured mature birch stand (effective plant area 3.6 to 5.8) puts 3 to 11% of the floor in fleck at this sun; a thinner stand, at an assumed 2, up to 29%. In the shade, light from the leaves matches or beats the sky, and is far greener: the canopy is a second sky. Noon shafts are 15 to 20 times weaker than at golden hour, so they show only in haze. *Needs:* the leaf stage from the date; canopy openness kept as optical depth, so the season scales it; the canopy's radiance filling the covered part of the sky; flecks from a canopy light map, with sharp leaf shadows only in cascade 0; leaf translucency inside the one shade function; the ground bounce through the canopy; exposure adapted at the camera's place. *Terms:* canopy light map (sun step), canopy openness (fact, read per pixel), canopy radiance (frame), flecks (px, 1 to 2 taps), translucency (px, leaves only), beams (px¼).

**3. Open heath in drizzle.** Wednesday 8 November 1989, 12:30 CET, on the heath above the town. Full low stratus, drizzle, a south-westerly wind; the sun hidden, 14.4° high in the south. There is no sun term, so the sky is everything. It is brighter at the zenith than at the horizon, and brighter towards the hidden sun. A standing stone has a lit side: debt 1's case, in the open. Nothing occludes but the land. The horizon is kilometres off, and aerial perspective and rain fog carry the depth. Wet heather and rock darken by porosity. The risk is mud: low value contrast and grey-brown bases. *Needs:* the CIE overcast sky with a sun indicatrix; the land's horizon from the height-and-sky map, not the town's; air density from the rain rate; the value bands and the white chip; how much chroma the shade keeps, as a key. *Terms:* sky (sun step, then px), height-sky (fact), air (px), water profile (px). The cheapest case.

**4. A dense street at night, many lamps in view.** Thursday 14 December 1989, 19:00 CET, the sun 23° below the horizon. Low stratus, wet after rain, shops open late before Christmas. Sodium street lamps, an older street of mercury, White SON in a new pedestrian street, neon signs, lit rooms: 60 to 150 lamps in view, and later a metropolis. The sky is orange-grey from the town's own light on the cloud base, up to ten times as bright as a clear night's, and brightest over the densest lamps. Sodium drains colour, so brick and green paint go to near-identical browns. Puddles double the lamps, and halos grow with the rain. *Needs:* lamps by circuit; one lamp list, with the tier chosen per frame (shadowed near; unshadowed, in our own binned buffer; coronas and ground pools far; glow on the cloud base farthest); a rendition matrix per lamp kind; GGX lamp highlights with an emitter radius, and puddle sprites for far lamps; binned halos; the night sky from a cloud-glow map; exposure from a few lux and the eye's shift to blue, as perception keys. *Terms:* tiering (frame, CPU), lamp loop (px per binned lamp, plus nine multiply-adds for rendition), town light map (fact, until a switch), cloud-glow map (frame), static shadow slices (fact), movers (frame).

**5. Snow at low sun.** Wednesday 15 February 1989, 15:30 CET, the sun 11.6° high at 220°. Clear and cold after a night's snow, 8 cm lying, dry air. Snow at about 0.9 albedo throws light up into every shaded face; shade on snow goes blue from the sky. The sun is warm and low, and long shadows cross the town from the far stop. Snow glints, and in deep cuts glows faintly blue. White must stay white without clipping. *Needs:* snow lying as a fact; snow on each surface from its weather exposure; ground albedo by cover in the seen-ground bounce; a clear sky from a model; one derived sun colour for every reader; far shadows from the horizon angles; glints and translucency as material data; exposure from illuminance, checked with the chart. *Terms:* snow (px, no extra reads), seen ground (px, 1 to 2 taps), far shadows (px, against a fact-clock map), sky (sun step, then px).

## The check

Each need, line by line, is set against the record L1 plans (layers 1 to 3 of `lighting-and-colour.md` §8, drafted below) and the shade's terms. Term numbers are from today's code (see Today's code). "Hold now" means L1 must fix it in the format; "add" means a later stage adds it without changing what exists.

Cost classes, after `docs/research/performance-craft.md` §2's clocks:
- **px**: per pixel, every frame (the camera's clock). **px½, px¼**: per pixel in a reduced pass.
- **vtx**: per vertex.
- **frame**: per frame, as uniforms or one small map (the clouds' clock).
- **sun step**: cached, rebuilt at a step index computed from absolute time (about half a degree of the sun), the two neighbouring steps cross-faded, so the result never depends on the path taken.
- **fact**: cached until a fact changes: the town, a tree, the season, a switch (the history clock).
- **offline**: pack tables, computed once.

| # | Need | Cases | Record holds | Shade term | Today | Class | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | One date, instant and place | all | `world`, the world state embedded, with a sub-second instant | every term | three clocks: the rig's date, its `clock`, `_OS_Date` | frame | **hold now** |
| 2 | Sun direction, colour and illuminance through the atmosphere | 1, 2, 3, 5 | `derived.sun` | 11 sun, 13 warm turn, beams, clouds, sky | direction derived; colour and strength typed; 3.0 for the Light, clamped to 0.45–1.4 for clouds and beams | sun step | **hold now:** one sun for every reader |
| 3 | Sky radiance from a model: twilight (1), clear (2, 5), CIE overcast with indicatrix (3), under the town's glow (4) | all | `derived.sky`: model id and parameters, with L2 SH (9 × RGB) derived from them | 4 sky colour, from SH | four typed colours and a sun-side horizon | sun step to project; px, 27 multiply-adds | **hold now** the slot; the models come in L6 |
| 4 | The same sky in reflections, the dome and probes | 1, 3, 4, 5 | `derived.sky`'s parameters, the one source of all three | 16 reflections; the sky dome | the dome typed apart from the ambient; a sky-only probe | sun step (probes relit at the step) | **hold now** |
| 5 | Sky seen, bent normal, horizon of town and land | all | `derived.maps`: height-sky, by input hash | 5 town sky, 8 bake | 64 reads a pixel, town only | fact (pages P0.B, P1.R, bent normal: reads already paid) | fits; performance item 2 moves it |
| 6 | Sky through leaves: canopy openness as optical depth × leaf state | 2 | `world`'s date → leaf stage by the pack's phenology; thinning and dieback are tree facts; `derived.maps`: canopy, a world-space layer beside height-sky | sky term, canopy share | `_Season` typed per tree material | fact (page P1.B, and the canopy layer for the air, adaptation and woods without pages) + px, one `exp` | add, if the sky-seen bake excludes crowns now |
| 7 | The canopy's radiance, the second sky | 2 | `derived.canopy`: one colour per species and stage | new: fills the covered part of the upper sky | `_Through`, a light colour per material | frame | add |
| 8 | Sun flecks; near leaf shadow | 2 | `derived.maps`: canopy-light, with its step | 11 sun × canopy transmittance; leaf detail in cascade 0 only | leaf cards in every cascade | sun step (a 256² map; a noon fleck moves its own width a step, so neighbours cross-fade) + px, 1 to 2 taps | add (1e) |
| 9 | Leaf translucency | 2 | material data: τ RGB and thickness by stage | 24 translucency, moved into `OS_ShadeP` | the tree's own shade function, 16 floats | px, leaves only | add (1e); the second shade function retires |
| 10 | Seen-ground bounce, with albedo by cover: forest floor, wet heath, setts, snow | 2, 3, 5 | nothing per place: cover from the ground map, albedo from the pack's table, wet and snow from `world` | 7 ground light, rebuilt as L8's lookup | a third albedo in every weather; a facing guess | px, 1 to 2 taps | fits L8 |
| 11 | Snow lying, and on each surface | 5 | `world.snow` (new: depth, age) | the water and weather layer, from P1.G | absent | px, no extra reads | add (plan step 9) |
| 12 | Snow glints and translucency | 5 | material data | specular; the translucency term shared with leaves | absent | px | add (plan step 9) |
| 13 | Far shadows at low sun | 5, 1 | `derived.maps`: height-sky's horizon angles | 11 sun past the last cascade: the sun's elevation against the horizon angle towards it | four cascades to 200 m | fact + px, continuous in the sun | add (research item 9) |
| 14 | Cloud shadow and light; cloud base and kind; fog | 1, 3, 4, 5 | `world.weather`: cover, and new base height, kind and fog; `derived.maps`: cloud | 12 cloud light; 21 air | typed per rig; computed twice a pixel; drift 0; the sea-fog bank typed | frame, one map | **hold now:** the three fields, since L7 must re-express today's sea-fog rig |
| 15 | Air: layers by distance, density from rain and haze, darker and greener under trees | all | `derived.air` (global); place variation from the maps; keys per layer | 21 air; beams | eighteen typed settings | px; px¼ beams | fits; density derived |
| 16 | Which lamps are on | 1, 4 | `derived.circuitsOn`: street circuits only. Shop and room light is derived from people's habits (`sources.people`) | 14 lamps; 17 emission | `lampsOn` per rig: off at the 17:50 blue hour, on in the 17:50 sea fog | per event | **hold now:** by circuit, never typed |
| 17 | Lamp kinds: colour, flux, rendition, warm-up | 1, 4 | `sources.pack`: one kind table; output now from schedules and absolute time | 14, plus a 3 × 3 rendition per kind | sodium in three colours in three files | offline + px, 9 multiply-adds per lamp; warm-up per frame, CPU | **hold now:** one table |
| 18 | Many lamps: the tier per frame, our own binned buffer | 4 | nothing: tiers are per camera, set by the renderer | 14 reads our buffer; URP lights only for shadowed lamps | URP Forward+, capped at 256, on 64 px tiles | frame (CPU) + px per binned lamp | **hold now:** no tier or budget in the record; stable lamp ids |
| 19 | Lamp shadows: static slices cached, movers per frame | 4 | lamp facts: static or moving; a change stamp per town cell | 14 shadow | no lamp casts | fact + frame | add (the night step) |
| 20 | Lamp highlights in wet streets | 1, 4 | part data: the socket's emitter radius | 15 lamp specular, as normalised GGX | unnormalised Blinn-Phong, about twenty times too dim | px per lamp | add (the night step) |
| 21 | Halos in fog and rain | 1, 4 | `derived.air`; the halo key | `FogLights` | every lamp at every pixel | px per binned lamp | fits once binned |
| 22 | Town light map: ground pools, upward flux, the mix's rendition | 4 | `derived.maps`: town-light | the far tier's ground term | a glow map | fact, until a switch | add |
| 23 | Night sky under cloud, from the town | 4 | `derived.maps`: cloud-glow; `derived.sky`, model "night", its SH from the map's mean | 4 sky term; the dome | typed; the town's glow lights cloud undersides only | frame | add the map; the sky's slot holds |
| 24 | Moon and stars | 4 on clear nights; June nights | `derived.moon`, from the date | a second directional term at night | absent | sun step | add |
| 25 | Lit windows, room by room | 1, 4 | the rooms' facts and the people's habits, through `sources` | 17 emission; interior mapping later | typed window glow; per-window warmth from the bake's alpha | px | add; warmth from the room's facts |
| 26 | Exposure from illuminance, adapted at the camera's place | all | `derived.exposureEv100` (global); a bias key | post | typed `postExposure` | frame | **hold now:** global in the record; adaptation local, and reset on a time jump |
| 27 | The eye's shift to blue at night; how far lamps drain colour | 1, 4 | keys, by adaptation luminance | grade, shade chroma | absent | frame | add keys |
| 28 | Art keys that hold across seasons and latitudes | all | `sources.keys` (hashed); `derived.keys`: elevation, morning-to-evening weight, weather weights, resolved pushes | — | typed per rig, per hour | frame | **hold now** |
| 29 | Debug views of every term | all | — | one view per term id | `_OS_Debug`: UV, normal, position, distance, smoothness | — | **hold now:** views from the term registry |

**The cost of the range.** The per-pixel additions are few: one or two taps each for the fleck map, the seen ground and the town light map's far pools; the far shadows compare against horizon angles the town-sky term already reads; per lamp, a profile tap and nine multiply-adds. P1.B and P1.G are read already, and the cloud map replaces seven noises with one read. The lamp loop is the only per-pixel cost that grows with the scene, which is why it must leave URP's Forward+ for a buffer we bin and cap (row 18). Everything else is a colour per frame or a map rebuilt on the sun's or the town's clock.

## What L1 must hold

1. **One clock.** The world state is the record's first layer, embedded and hashed, with a sub-second instant beside `timeOfDayS` so a frame can be replayed. The rig's date and `clock` and `FabricDate` become readers of it. A transition is the world state changing; two records are never blended.
2. **Inputs make the identity.** The record's hash covers the world state and the sources: the fabric (buildings, trees, lamps, circuits, rooms), the people's habits (who lights which room, which shop is open), the pack's tables, the key set and the derivation function's version, plus the overrides. Derived values, the key coordinates and resolved pushes among them, are stored for diffing and checked within a tolerance on load, never hashed. `schemas/hashing.md` hashes a float by its bits, and Python and C# may differ in the last bits of a sine, or round a millidegree apart.
3. **One sun.** Its colour and illuminance are derived once. The Light, the clouds, the beams and the sky all read that value. Keys push it, and no reader clamps its own copy.
4. **One sky.** A model id and its parameters. The ambient's L2 SH (nine RGB coefficients), the dome and the reflection probes all derive from them. Today's hemisphere colours become a view of the SH. The sun's disc and halo stay terms of their own, out of the SH.
5. **Lamps by reference.** The record holds the sources' hashes and the street circuits on now. Never a lamp list, a tier or a budget. Shop and room light is derived from the habits. Lamp ids are stable.
6. **One lamp kind table** in the pack, referenced by hash. It holds colour from the spectrum, efficacy, the rendition matrix and warm-up. A lamp's output now derives from its schedule and absolute time. It replaces the three sodium colours.
7. **Nothing that depends on place or camera.** Whatever varies across a frame (ground cover, cloud glow, canopy, town light, the fog bank) lives in a map. The record holds only global quantities and small tables by kind (the canopy's radiance per species and stage).
8. **Maps by id and input hash.** The maps are height-sky, canopy, canopy-light, cloud, cloud-glow, town-light, the reflection probes and the colour table, each registered in `schemas/maps.json`, which owns its clock. Sun-step maps are built at a step index from absolute time, with the two neighbours cross-faded, and the step is recorded in the entry. A new regime adds an id.
9. **Keys by the sun's elevation.** They are keyed by its signed elevation (clamped at −18°), a continuous morning-to-evening weight (from the sun's hour angle, equal at the day's highest and lowest points, so December's noon and June's midnight never jump), and weather weights. Never by the clock hour. June's light nights then take the blue-hour key at −7.6°, which is true, and December's 15:00 takes the low sun's. Pushes are OKLCH deltas on named targets; overrides are sparse, by place.
10. **Exposure split, warm state named.** The global EV100 from illuminance and the bias key are in the record. Some state warms up over frames: the eye's adaptation at the camera's place, and the probes relit a few a frame. It is camera-local, outside the record, and resets on a time jump, so D10.7's time-jump test holds.
11. **Room to grow.** Blocks for regimes not yet built (moon, canopy, snow) are optional. An absent block means "off", and is never written zeroed, so two files hash alike. Adding one goes as "2, unchanged, no migration" in `schemas/CHANGELOG.md`.
12. **One registry of terms.** The keys' targets and L1's debug views come from the same list of term ids, so a new term arrives with its key target and its view.
13. **Units and names.** A signed millidegree definition beside `record.schema.json`'s 0 to 359999, with names spelled out (`elevationMillidegrees`, as `fromMillidegrees`); circuit ids with a prefix in `schemas/naming.md`; photometric values as floats, since they span a starlit night to noon snow and are never hashed.

## The record, drafted

This goes only as far as the check needs. L1 writes `schemas/light-record.schema.json` from it.

```jsonc
{
  "schemaVersion": 2,
  "world": { /* world-state.schema.json, embedded. L1 adds: a sub-second instant;
                weather.cloudBaseMm, weather.cloudKind, weather.fog (visibility, bank top).
                Plan step 9 adds snow { lyingMm, ageHours }. The sun and moon are
                derived from date, instant and place, never stored. */ },
  "sources": {                       // hashed, with world and overrides
    "fabric":   "<hash: buildings, trees, lamps, circuits and rooms at the fabric date>",
    "people":   "<hash: the habits that light rooms and open shops>",
    "pack":     "<hash: lamp kinds, leaf optics by stage, phenology, albedo by cover, sky model constants>",
    "keys":     "<hash: the key set>",
    "function": "light-derive-1"
  },
  "overrides": [ { "place": "<placeId>", "pushes": [ /* as derived.keys.pushes */ ] } ],
  "derived": {                       // stored, diffed, checked within tolerance; never hashed
    "sun":  { "azimuthMillidegrees": 258000, "elevationMillidegrees": -4900, "illuminanceLux": 0.0, "rgb": [0, 0, 0] },
    "sky":  { "model": "twilight", "params": { /* the model's own */ }, "sh": [[0.0, 0.0, 0.0] /* × 9 */], "illuminanceLux": 10.0 },
    "air":  { "phaseG": 0.7, "layers": [ { "toMm": 30000, "density": 0.0, "rgb": [0, 0, 0] } ] },
    "keys": { "elevationMillidegrees": -4900, "evening": 0.99, "weather": { "clear": 0.4, "overcast": 0.6 },
              "pushes": [ { "target": "air.far", "dL": -0.020, "dC": 0.015, "dh": 0.0 },
                          { "target": "exposure", "dEv": -0.3 } ] },
    "circuitsOn": [ "ci-street-photocell" ],
    "exposureEv100": 2.0,
    "maps": [ { "id": "height-sky", "inputs": "<hash>" },
              { "id": "cloud",      "inputs": "<hash>" },
              { "id": "town-light", "inputs": "<hash>" } ]
    // optional blocks, absent when off: "moon" { azimuth, elevation, phase, illuminanceLux };
    // "canopy" { "stages": [ { "species", "stage", "radianceRgb" } ] }
  }
}
```

## Outside the record: formats that must hold too

- **The page bake** (`docs/building-blocks.md`, P0 and P1): sky seen must exclude tree crowns, and the canopy's optical depth at full leaf goes in P1's reserved B, so the season scales it by one multiply. Trees baked into other parts' sky seen would freeze the season. A world-space canopy layer beside height-sky serves the air, adaptation and woods without pages. To be checked when the birch chunk validates (port step 4, `reviews/lt1/port/foundation-needs.md`).
- **Light sockets on parts:** position, aim, an emitter radius, a distribution profile id, an upward light ratio, a static-or-moving flag and a stable lamp id.
- **Lamp and room records:** kind, circuit, watts, era, upkeep, time since strike. A lamp that cycles or warms up is history, and reads as such.
- **Material data:** translucency (τ RGB and thickness) as one field for leaves, snow, curtains, paper and sailcloth; glints for snow; no light colour of their own.
- **Tree records:** crown lobes, height, leaf area, clumping and leaf angle, with leaf state and dieback as facts. The fleck pattern may be seeded only for small gaps, inside the crowns as projected along the sun. A big gap (a dead limb, a felled neighbour) is history and must come from a fact.

## Today's code against the format

From a read of `StreetSurface.hlsl`, `StreetLooks.hlsl`, `Tree.shader`, `Code/Scenes/` and the five rigs in `Experiments/LT1/Heart/Light/`, at `fefec2f` with W4's `5465bfe`. These are not LA's to fix; L1 and L7 retire them.
- **24 terms:** 22 on the street and stone path, and 2 in the tree's own shade function, which keeps 16 shade floats and `_Through`, a light colour, per material.
- **76 rig fields:** 9 inputs, 2 derived (the sun's bearing and elevation) and 65 typed, 17 of them colours. 3 are dead: the shafts' reach, decay and threshold feed a pass that is in no renderer.
- **Nothing reads the world state.** Precipitation's kind and rate are absent, and the season is typed per tree material.
- **Lamps are anonymous.** `lights.json` holds a position, an aim and a kind for each of 403 lamps, with no id, schedule, era, socket or condition.
- **The town-sky lookup** runs per pixel in three shaders, and the cloud light is computed twice a pixel.

## Open unknowns, and where each is learned

| Unknown | Where it is learned |
| --- | --- |
| Whether derived floats agree across Python and C# within the tolerance | L1, with golden vectors beside the hash vectors |
| The sun step's size, and the cross-fade's cost and look on the canopy map | L1 for the rule; 1e for the canopy map |
| Whether L2 SH holds a twilight sky's bright west and a clear sky's sun side without ringing | L6, against the model evaluated directly |
| Whether horizon angles give far shadows sharp enough at the far stop | research item 9, with performance item 2's horizon map |
| Milliseconds per lamp in `OS_ShadeP` on the M4 at 32, 128 and 256 lamps, URP Forward+ against our buffer | an Xcode trace of Harbour Row at night (`performance-craft.md` item 3), before the night step |
| Whether a kind index can ride on URP's own light data, or needs our side buffer | a spike at the start of the night step |
| A shadow slot's cost at 8 and 16, and a cached static slice in a Render Graph pass | a one-day spike in the night step |
| The canopy light map's cost, and whether URP's main-light cookie can carry it | 1e, the birch rebuilt (Q16) |
| West-coast birch leaf area, clumping and openness; leaf spectra by month | 1e's subject research (the leaf spectra datasets are a download, waiting for Øystein's OK) |
| How Firewatch built its trees' light and shafts | Jane Ng's GDC 2015 talk, watched before 1e |
| Kyba's cloud-glow factors for a small town in 1989 | calibrated against photographs in the night step |
| Whether snow needs its own key, or derives fully | plan step 9, weather |
| Local exposure adaptation under trees and in lamp pools | L4 |
| Whether noon shafts under birches show at all without a haze fact | the beams' quarter-size test, reading the canopy map, in 1e |
