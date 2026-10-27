# The walked corner: art direction

Øystein, 27 October: "Stylisation means deciding what matters, pushing that harder than reality does, and removing almost everything else", and "Heavy things should look heavey, lived in things should look lived in." This page sets the corner's style as rules for each element. The engine frame shows it. Each element is then built and judged in the corner against both, one at a time: the light first, then the houses, the rock and ground, the lamps, the growth and the trees.

**What matters** (27 October; painterly realism in VD1's line, stylised hard: decide what matters, push it harder than reality, remove almost everything else)
1. **One focus:** the Landing lantern by C's lit corner. Every value, edge and detail serves the eye's way there.
2. **White timber against dark wet rock**, the frame's largest contrast, kept for the focus. The gully is steeper and tighter than it measures: its walls one dark simple mass, the flight a ladder of wet lit noses up to the Landing.
3. **Sea fog in three clear layers:** the near clear, the Landing veiled, the far town one flat silhouette in the fog's colour. The air carries the hour's colour.
4. **Warm in a cool hour:** each lamp a small hot head, a tight halo and a long streak mirrored in the wet stone under it; lit windows the only other warm. Nothing else is warm.
5. **Clapboard as rhythm:** a few bold shadow lines near, lost in shade and gone past 12 m.
6. **History as designed shapes from the coat data,** such as a peeled patch or a renewed run, never noise. True colour only where people keep things (D's pantiles, a door). The rest is muted grey-blue, as in Stålenhag's world with its one or two kept accents.
7. **Removed:** mottle, grain, texture noise, small clutter, every line that carries no fact, and detail away from the focus and the history. Edges are found against the sky and at the focus, and lost inside shade.

## The frame

[engine/street-1750-sea-fog.png](engine/street-1750-sea-fog.png) is the street camera in blue hour with sea fog. It renders in Unity at 2560×1440 (2× supersampled, 4× MSAA), with [-grey](engine/street-1750-sea-fog-grey.png) and [-eighth](engine/street-1750-sea-fog-eighth.png) beside it.
- **How it is made:** `LT1ArtPasses.Paint()` stages the corner, then swaps every renderer for `ArtDirection/PaintSurface.shader`. One full-screen pass, `PaintAir.shader`, adds the air, sky and halos. Every value is in `ArtDirection/Paint.json`. No shared file is changed.
- **Fable's verdict** (27 October, before the last pass): "Direction right; frame not yet its proof". L\* runs from 5 to 95 with a median of 30, a true blue-hour histogram. The frame is its own: white timber on wet rock is not Stålenhag's motif, and it borrows only his restraint and air. The last pass fixed what Fable and the coordinator found worst: the sky without the hour, the tufts, the stair's equal warm rims, the split focus and the vinyl clapboard. One unexplained warm wash, about 74, stays on C's east face near the lamp even with the lamp at zero: the light's rebuild should find it.
- **The geometry is still greybox.** The knuckle, the retaining walls, the banks and the ground are clay. The knuckle reads as a box with scratches, not rock. The lantern is a simple frustum. The frame judges the style, not these.
- **VD1 holds.** This stays painterly realism with Stålenhag leading. It sharpens VD1 with the removal rule, the one focus, and weight and use as the material rule. Two earlier routes were not picked: the ink stylings in [styles/](styles/) (print, silver, two inks, and the merged kept print) and the code paintovers in `frames/`. Paintovers on clay passes could choose between ideas, but they could not show a style. The ink routes gave way when Øystein kept the Stålenhag line.

## Every element

- **It reads as what it is:** its weight, its use, its age and its care.
  - **Heavy things** sit into the ground: a denser, darker foot, contact shade, thick edges, big blocks low and small ones high, and a shadow under every lip. Nothing heavy is thin-edged or floats.
  - **Light things** (posts, railings, gutters, glazing bars) are slender, crisp and lifted off their ground.
  - **Wear and care come from facts only:** wear where people act (treads dished in the middle, thresholds, door paint by the handle), kept things kept and let-go things let go, by the coat data. Nothing invented.
  - **Wet things are dark with sharp reflections.** Old things have softened arrises and settled lines.
- **Matte unless wet.** Limewash, oil paint, timber, dry stone and rock carry no sheen. Only wet stone, wet ground, wet roofs and glass reflect.
- **A few broad value shifts per surface, never noise:** a wall darker and cooler at its foot, a few long streaks under sills, up-facing planes lighter (Carlson's angles).
- **One signature mark per material, drawn big:**
  - timber: the board shadow line;
  - cut stone: its joints and the dark wet margin;
  - rock: a few faceted planes and cracks;
  - pantiles: the wave along the courses;
  - growth: its silhouette.

  Nothing looks made of the same stuff unless it is.
- **Contact shade at every junction,** where a wall meets the ground, a plinth meets rock, a step meets a cheek wall, or a house meets its plinth.
- **Edges and detail fall away from the focus.** Edges are found at the focus and against the sky, and lost inside shade. Marks show in full at the focus, are gone past 12 m, give way to shapes and lights past 50 m, and to silhouettes in the air past 130 m.
- **Facts:** lamps, lit windows, wear, growth and wetness come from the record, or they are not drawn.

## The light: a target per light

L\* as measured on a frame, with today's real-scene still against it. One wetness per moment, from the record, holds for every surface.

| Light | Sky | White, lit / shade | Darks | The one accent | Today |
| --- | --- | --- | --- | --- | --- |
| **Blue hour in sea fog** (17:50) | Deep blue ~30 overhead, grading to a cooler, luminous band at 55–60 over the gully's top | The lantern's reach on C's corner ~70, falling to C's shade 50–55 by the second window | Shade pools 8–15, darkest 5 | The Landing lantern's head, the only 95. Its halo is gone by 3 m. Windows 60–70. Nothing else above 85 | C's front 17, the far fog 26 and blue, the sky 39 |
| **Drizzle** (13:00) | ~72, the lightest field | 78 / 60 | 10; wet rock tops 40 | True colour: D's wet pantiles, a dull burnt orange darker than its wall | Walls 26–36, sky 65, wet treads 22, D's pantiles grey-blue (h 277) |
| **Low sun** (16:00) | The sky's blue in every shade | 88 / shadows 30 | 8 | The sunlit gable corner at the Landing and one wet streak | Shade 26–49 and magenta (h 320–338), lit walls 64, sky 62 |

**Hue.**
- **Blue hour:** the shade is slate blue (h 245–250, low chroma), and the lit fog a warmer grey-violet. Warmth comes only from the lamps, their reach and the lit windows.
- **Drizzle:** silver-grey, with the true colour of kept things the only saturation.
- **Low sun:** gold on what faces the sun. The shade takes the sky's blue, never magenta.

## Each element

**The light (first).**
- It is designed, not simulated:
  - a sky light by the normal (up, side, down);
  - each lamp's reach as one designed shape (a fan on a wall, a streak on wet noses), falling off by 3 m;
  - the fog in three distance steps;
  - halos hidden behind what stands in front of them;
  - contact shade.
- The light's job is to hit the targets above in the real scene and close each gap from today.

**The houses.**
- **Form:** a pale painted body on a heavier stone plinth. The two faces are about 15 L\* apart. Trim and sills are the found edges. A roof is one plane against the sky, darker than its wall in every light. Chimneys are crisp small darks.
- **Material:** matte. The mark is the board shadow line, bold at the foot and where a lamp or the sun rakes, and gone past 12 m. Each wall is darker at its foot, with a few streaks under the sills from the mesh's own run-off and the coat's age.
- **Values:** the plinth sits a half-step above the rock, with contact shade at its top and at the ground. True colour on kept things only.
- **History:** whole shapes from the coat data, such as a peeled patch or a renewed run of boards.
- **Still missing:**
  - honest irregularity on old timber (a slight ridge sag, uneven boards, seeded, claiming no history);
  - a mark for C's slate;
  - a pantile roll and course length from the covering's record, not generic.

**The rock and ground.**
- **First job:** real faceted mass. The knuckle and the retaining walls are clay forms, and painted cracks cannot fix that (the gully's stones may lend it form).
- **Form:** a few big facets along real jointing, never blobby. Rock is rigid, so it is only moved and turned, never bent.
- **Material:** dry is matte, wet is a mirror. The mark is a few planes and cracks, and the wet streak under a lamp. Stone walls batter where that is true of them, with big blocks low and a dark wet margin at the joints.
- **Values at blue hour:** tops 22, faces 11, foot 6 (the densest dark). Deep shade where the rock meets the steps. The ground 15.
- **The steps:** three value groups rising up the flight. Lit noses only in the streak under a lamp, dark between them. The one mark is the worn hollow in the middle, from the steps' wear fact.

**The lamps.**
- **Form:** a small head on a thin post. The lantern needs its real form: a bracket and glazing bars.
- **Values:** the focus lamp's head is the only 95. Other lamps are lower, with smaller halos. Halos are tight near, and wider and dimmer layer by layer in the fog.
- **Light:** one designed shape per lamp. Its colour comes from the lamp's kind.
- **Facts:** lamps are kept infrastructure and read as history, so each comes from the record or is not drawn.

**The growth.**
- The fact on the knuckle and the wall is lichen. It shows as flat crusts that follow the rock: matte, within 5 L\* of their surface at blue hour, with a broken edge against the sky. Never mounds.
- Heather or grass only where the record puts soil (heath above E, since 1958; weeds in D's yard, since 1986). Spiky, varied silhouettes, never round blobs.

**The trees.**
- Three to five masses, never leaves, with their crowns lost upward.
- Values: silhouettes at the fog's value plus 5. Near trees are darker, with one lamp-lit side.

## What carries over to the light's rebuild

- **As is, from `ArtDirection/Paint.hlsl`, `PaintSurface.shader` and `PaintAir.shader`:**
  - the sky gradient, the fog colour and the lit glow;
  - the hemisphere sky light by the normal, with a calm factor per surface;
  - each lamp's soft fill;
  - the wet streak (a lamp's mirror image stretched along the view);
  - the rounded wet-edge catch on noses;
  - halos with a depth test;
  - the worn-path rule (gloss and value by distance from a centreline, from a fact);
  - the pantile and sill marks, which read the house mesh's own UVs.
- **As a pattern only:**
  - the three fog steps with a veil per surface (per kind in the real scene);
  - the found edge against the sky (needs a depth pass);
  - the contact shade (needs TAA or a blur at native size);
  - slots and masses by street boxes, which stand in for kinds;
  - the mass feet and crack lines as data, which belong in the rock and ground's kind data.
- **`Paint.json`:** its structure carries over (globals, surfaces, lamps with fill and catch). Its numbers belong to this one moment.

## What the frame must not claim

- Only the Landing's 1955 lantern is drawn: the record (`fixtures/lt1-corner.json`, `lt1-town.json`) has no other lamp on the flights.
- Lit windows come from the house mesh's seed, not from the engine's occupancy. No blind test uses them until the engine provides it.
- The worn path is centred, or its side comes from data.
- Wetness is one per moment, from the record.
- The cracks and the darker feet are non-semantic and claim no history.
- What would make it remarkable, from facts only: the wet rock beside the lantern mirroring it in one long streak, and one trace of a person at the focus (a bicycle, a doorway's spill) when the record holds one.
