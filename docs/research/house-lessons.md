# Houses: what we learned before starting again

28 October 2026. Øystein: start the building "completely from scratch ... not removing our learnings". The old house code, the town's houses and their stills left HEAD on this day; they are in git (house 109 to `3818182`, the town to r36, the hero houses to `ee5bee5`). This page keeps what they taught. How games build a house is in `house-asset-craft.md`; the town's rounds and their lessons stay in `reviews/lt1/town/README.md` and `method.md`.

## Why it read as CAD

- **No finishing.** Every surface was one clean coat from a procedural shader. The band every reference keeps, marks 10 to 50 cm across (board-to-board value, a repainted run, a dirty foot, streaks under a sill, paint lost in groups), was missing, and our fine marks faded before the street stop. In grey, 109 read as equal boards, straight lines, one value from foot to eave.
- **Too many triangles in the wrong places.** 109 was 52,600 triangles near, 10,700 at the street. Games put a low-density house at about 8,000 and spend on chamfers and silhouette, not on modelled flakes.
- **Exact and straight.** Formula parts with ridge sag capped at 50 mm and board tilt 1.6 mm, both under 3 px at the street stop, so nothing bent that the eye could see.
- **Flat edges.** Chamfers of 4 to 10 mm, flat-shaded, near only. An edge catches light only from about 2 px: 8 mm at 8 m, 20 mm at 20 m.
- **No texture space, no bake.** Occlusion was one linear field per board, never pooled into corners; the far levels were boxes, not made from the near house.
- **Judged in the wrong place.** Houses were judged inside a broken town or tuned to one camera. Light and air could not carry boxes (the town's step 1, r34 to r36).

## What held, and stays

- Massing from the house's record: body, lean-to, arks, porches, roofs over the combined footprint, pitch and eave by era. Architecture from facts is our strength.
- History only from facts (`docs/upkeep.md`, UK4). A diary's named event wins over any rule: 109's 1960 ox-red repaint stands, and an unlived warehouse is kept as if neglected.
- The shared rules of `reviews/lt1/town/method.md`: one shape language, one light, one value plan (walls palest, roofs darker in every light), one distance rule, one edge rule. No photo noise, no fine noise, no uniform jitter.
- Clay first, colour last: each material at its own lightness in grey, with real relief and gloss, until a clay ensemble holds.

## Measures worth keeping

- At 1440p one pixel spans 0.48 mm per metre of distance. A 10 to 20 mm lap step is 1 to 2 px at the 20 m street stop.
- Stavanger's surrounds: side boards 120 to 125 mm wide and 25 mm thick, the window set 30 mm in, water boards 30 mm thick projecting 120 and 180 mm. Old barge boards 28 to 34 by 195 to 220 mm. Classical houses have almost no eave (about 140 mm); sveitser houses deep ones.
- Board widths vary to fit openings. Only mass-made things repeat (tiles, slates, catalogue brackets).
- The silhouette (ridge, chimneys, eaves, barge boards) is judged first, black against the sky, in grey light.

## How to judge

- Four views every time: eye level, the street stop, 12 m, high. Nothing goes to Øystein that the coordinator has not looked at from all four.
- Grey light first, then one light. Beside the references, never beside our own earlier work. If it is bad, say bad first.
- When a look won't converge, stop tuning: fix or redraw the part itself, one change at a time.
- Fewer, bigger, designed steps, each looked at before the next. The town ran eighteen tweak rounds after "no new models" was agreed, and nobody stopped it; every session is watched.
