# The sea at the shore

How to build the water at the Holm tip, where the Roads meet banded phyllite whalebacks and a plucked lee. Research for Nature 2 (water), 29 October 2026. It fills the gaps in `land-rock-and-water.md`, section 3, and does not repeat it. Marks: (unverified) means no source confirmed it; (ours) means our own arithmetic.

## In short

1. **The tip is a small-wave, sheltered shore.** The Roads give 0.28 m waves at 10 m/s, running 0.6–0.8 m up the slabs (ours, from EurOtop). An annual storm sets still water at +0.79 m MSL (Kartverket) and adds 1.4–2.1 m of run-up. The rock code's storm top, 3.6 m over high water, needs the fjord's 10 km of fetch on the north face, and is too low on the sheltered sides, which the surge reaches too. Both fetches count as "sheltered" (MarLIN), so the bands differ between sides by decimetres. Drama must come from storms, shape and light.
2. **No shipped game documents foam on rock** (Horizon calls it future work). What has shipped: a baked shore field (Croakwood, Crest, Dredge), wavefront curves (Horizon), hand-made foam meshes and a wet band moved by a sine (RiME), spray fired by rule (Sea of Thieves), and only the line where things meet the water (Bad North).
3. **How a wave meets rock follows from the slab's slope** (EurOtop): it plunges on 1:3, collapses on 1:2 with the largest run-up, surges on 1:1, and reflects off a vertical step. The slopes are in the rock parts.
4. **Wet rock is the water layer we have** (`Water.hlsl`), with the sea as a second source. Dark phyllite darkens only 20–30% (Lekner and Dorf; ours), so the film's gloss carries the read at grazing angles. It dries film first, from the edges, convex parts first (Lu 2005).
5. **On the M4 the sea must be nearly free**: opaque water, baked fields, a grid displaced at the vertices, few particles. The frame is over budget already; Metal cannot read depth in-tile, and URP has no tessellation.

## How the best build it

- **Horizon Forbidden West** (Malan, SIGGRAPH 2022).
  - One hand-animated breaking cross-section, stored as a texture, serves every wave. A compute shader deforms the mesh inside wavefront quads, and foam rides in the vertex colour.
  - Artists draw curves for the front and its break line, and a variation texture cuts gaps; one artist laid out every wave.
  - Triangles were never dense enough: splashes were toned down and foam under a triangle popped.
  - Ours is the curve tools; 0.3–0.45 m waves need no overhang.
- **Sea of Thieves** (Ang and others, SIGGRAPH 2018; Rare dev diary 32).
  - Foam forms on FFT peaks, and round objects by depth comparison in a window centred on the camera. It is feedback-blurred to disperse, then blended with painted textures. Calm water foams only round objects.
  - Spray fires by rule, from flipbooks filmed on Cornish rocks and filtered into the style.
  - No cost is published; the game runs on integrated laptop GPUs.
- **RiME** (Trümpler, Unreal Fest Europe 2018).
  - The water is unlit, coloured by a lookup on distance, with depth fade and Fresnel at the shore and a cubemap masked by Fresnel for reflection.
  - The shore foam is hand-made meshes ("nothing fancy"), and wet sand is a height mask moved by a sine.
  - The maths is mostly per vertex; "cheap".
- **Croakwood and Parkitect** (Texel Raptor, devlog 5).
  - Parkitect thresholds water against depth: cheap, but its foam cannot travel and shows only on the camera's side.
  - Croakwood renders what cuts the water from above and builds a distance field by jump flood, so its waves run shoreward.
  - **Crest** (docs) bakes a seabed probe and an optional distance field, "expensive" when live, and calls breaking shore waves an open problem.
- **Dredge** (Bastiaens, Unity 2025): one baked world "wave mask", its largest texture, sets the ripples, fog reach and depth. It uses sines because Gerstner crests launched the boat.
- **Bad North** (Stålberg, Konsoll 2018): flat water, drawn only where something meets it ("the coastline says water"). Its reflection is a mirrored copy of chosen objects.
- **Uncharted 3** (GDC 2012): normals flow along splines in two half-cycle phases.
- **Not found:** nothing primary on the shore water of Tchia, Ghost of Tsushima, Breath of the Wild, A Short Hike or Black Flag; Firewatch and Sable have no sea; the Last of Us Part II and Diablo IV talks are behind login.

## The constraints for us

**The facts.**

Kartverket's Stavanger levels, from MSL: MHWS +0.23 m, MLWS −0.23 m, highest astronomical tide +0.43 m; storms of 1, 10 and 100 years +0.79, +0.97 and +1.12 m. Highs are weather, not tide (Wolf and others 2023). The sides' exposure: north 1.0, west 0.8, east 0.35, south 0.1. The foliation strikes 160°, so on the north face its grooves run with the waves, and run-up and backwash should finger along them (ours).

Run-up is 1.8–3.0 times the wave height on smooth slabs (EurOtop 2018, equations 5.1 and 5.6); rock cuts it by up to half for small waves (Dodet and others 2018). Waves and run-up are ours, from JONSWAP and EurOtop:

| Water and wind | Waves | Run-up on 1:3 / 1:2 |
| --- | --- | --- |
| Roads, 10 m/s | 0.28 m, 1.9 s | 0.6 / 0.8 m |
| Roads, 25 m/s | 0.70 m, 2.6 s | 1.4 / 2.1 m |
| Fjord, 25 m/s | 1.28 m, 3.9 s | 2.8 / 3.8 m |

- **Not yet a fact.** Whether the fjord's fetch reaches the north and west faces is a fact of the map, unsettled. A storm top with the surge in it would read 0.57 m plus R times the exposure over MHWS: R ≈ 1.9 m with the Roads only, 3.3 m with the fjord (ours).
- **Recolonisation.** Barnacles and bladder wrack return in 1–4 years, knotted wrack in 7–15. Black *Verrucaria* first recruits after about 6 years and covers in 9–10 (MarLIN; Holt and others 1997, a Norwegian spill). So the 1882 cut and the ice-bare rock carry different bands.
- **The black band** (ours): north +0.6 to +1.2 m, east +0.35 to +0.55 m, south +0.3 to +0.45 m. A drift line laid at spring floods marks the top of the *fjæresone* (NiN 1.0).
- **For the rock code** (unchanged here):
  - Norway's big potholes are subglacial, only slowly enlarged by waves (Linge, SNL); `target_site.py` has the swell grinding them.
  - Salt weathering is about 0.6 mm a year on spray-wet greenschist (Mottershead 1989, 1997), about 6 cm a century (ours): no storm's mark.

**The views.** The rock lane's hero frame looks back at the tip from low on the water (`blender/parts/rock/kit/README.md`), where water is mostly reflection. A wet slab's film reflects 13% at 70° and 35% at 80° (Fresnel; ours).

At 1440p with a 35 mm lens a metre covers 700 px at 3 m, 175 at 12 m, 60 at 35 m and 17 at 120 m (ours). So 2–5 cm foam lace reads only within about 10 m. A 1 m foam band is a shape at 35 m and a single stroke at 120 m.

**The frame.**
- **Measured** (`reviews/perf/2026-10-27/frame-rate/`): MSAA 3.3–6.6 ms, SSR 0.8–4.7 ms, the depth texture and opaque copy 0–0.5 ms; the full frame at eye level is estimated at 21–23.5 ms.
- **Depth.** SSAO and SSR need normals, so a depth-normals prepass already writes `_CameraDepthTexture`. Opaque water drawn there, as SSR needs, sees its own depth, so its contact line must come from a baked depth, not a depth fade (ours, from URP 17.6's source). Metal cannot read depth in-tile.
- **A copy mid-frame under MSAA** stores and reloads colour, at most about 1 ms of bandwidth (ours, from Unity's Universal Renderer page and Apple WWDC20).
- **No tessellation** in URP, so waves need a dense grid centred on the camera. Discard loses Apple's hidden-surface removal; blending shades every layer. Spray uses the built-in particles; VFX Graph is not installed and unconfirmed on macOS.

**Style and the living world.** Hasui's few plates: the sky's colour, a darker body, a dark band under things, the lights' columns. Far off, soft marks, never noise; foam is as bright as the light and takes the sky's colour at dusk. Ref 54's far read: long thin white lines along the shore, over teal shallows and blue deeps. The tide is astronomical, so the wet line moves through the day. A storm is a dated event: it strips the wrack, throws a drift line, wets the rock to its run-up, and may hand the 1882 quay to upkeep. New rock starts its bands from its year.

## Approaches worth prototyping

**A. One baked shore field drives everything.**
- **The bake:** one texture over the tip from the rock mesh and the facts, at 0.25 m texels over 64 m (about 256 KB), holding the signed distance to the waterline, the depth to the rock, the exposure and the slope's breaker type (the Iribarren number).
- **Foam bands** travel shoreward on a phase, distance over wavelength minus time over period, both from the wind. Run-up climbs to the height its slope and exposure give.
- **The rock's wetness** comes from the same phase: the time since the last run-up, drying exponentially. It feeds `Water.hlsl` as a second source.
- **Cost:** one or two samples and no extra pass.
- **Who:** Croakwood, Crest, Dredge and RiME's band. Run-up and backwash on rock are new.
- **First test:** in the tip's grey-box scene, an opaque water plane against the north whaleback at the peak of a run-up, in overcast grey. Shoot it from the hero camera and from 35 m, beside t01's grey, ref 54 and a Hasui plate.

**B. Authored swash sheets and wavefronts.** Blender shrink-wraps a thin sheet over each seaward slab, its V running up from still water. A fall-line flow map follows the foliation's grooves, so backwash drains in fingers and cascades off the lee's steps. Wavefronts are strips bent round the headland, with Horizon's break line and gaps.
- **Cost:** a few thousand triangles and a thin band of overdraw. The sheets are drawn in full near, as lacing at 35 m, and not at 120 m, where A takes over.
- **First test:** the same camera and light, one slab with one sheet, at the run-up's peak and in backwash, at 3 m and 35 m.

**C. Painted plates and designed marks.** Two or three flat graded plates: sky, body, dark band. The foam is a designed border of a few widths along the waterline and the slabs' lips, changing in held steps as a painter repaints, never by smooth scrolling. Spray is one to three large soft shapes on exposed lips when the phase crosses them (Sea of Thieves' rule, with painted shapes).
- **Cost:** almost nothing. It is the far end of A and B, or a style of its own.
- **First test:** the 35 m and near-isometric frames in grey beside Hasui and ref 55, then the hero camera.

**The one still that decides:** A, B and C side by side from the hero camera and from 35 m, in overcast grey at the run-up's peak, beside the tip's best grey so far. A and C share one bake.

## The risks

- **Spectacle against fact.** Øystein asked for waves that thrill; the facts give 0.3 m most days. Invented surf breaks the facts. The honest routes are dated storms, the fjord's fetch if the map gives it, scale, and light on foam.
- **New work.** No game has shipped foam on rock or backwash off ledges: converge in grey, one change at a time.
- **Reflection.** URP's SSR is a preview in 6.6 and blocky on water at half resolution (Unity staff). A planar reflection is unmeasured on the M4.
- **Foam too fine.** Foam smaller than a triangle pops (Horizon); fine foam noise is the photoreal look.
- **Facts still moving.** The storm-top rule and the fjord fetch may change; the fields must read them, not copy them.

## Sources

**Water in games:** Malan, "Rendering Water in Horizon Forbidden West", SIGGRAPH 2022 Advances; Ang and others, "The Technical Art of Sea of Thieves", SIGGRAPH 2018 Talks, and Rare, Inn-side Story 32 (YouTube bJTYLZcqUqo); Trümpler, "Stylized VFX in RiME", Unreal Fest Europe 2018 (YouTube 4FIDBeF_4SI); Texel Raptor, Croakwood devlog 5; Crest documentation; Bastiaens, DREDGE, Unity 2025 (YouTube 1HO1U-d4G4c); Stålberg, Bad North, Konsoll 2018 (YouTube 6JcFbivo8dQ); Gonzalez-Ochoa and Holder, "Water Technology of Uncharted", GDC 2012.

**Coast:** EurOtop, 2nd edition, 2018; Dodet and others, JGR Oceans 123, 2018; Kartverket, station SVG, 1996–2014; Wolf and others, Frontiers in Earth Science 11, 2023; Lekner and Dorf, Applied Optics 27, 1988; Lu and others, Eurographics Natural Phenomena 2005; MarLIN, exposure, species 1330, habitats 104 and 120; JNCC biotopes 00000494 and 00000631; Kronberg, MEPS 49, 1988; Fróðskaparrit, Bruntse and others 1999, Fosaa 1987; NiN 1.0, article 3; Linge, SNL, "jettegryte"; Mottershead, ESPL 14 and 22.

**Cost:** Unity 6.6 manual; Unity Discussions, URP SSR preview, 2026; Apple WWDC20 sessions 10603 and 10632; Apple, Metal Feature Set Tables; URP 17.6 source.
