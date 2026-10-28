# Painted finish, round 1 (way P)

House 107's corner in 1989, painted as a painter would paint it. The model, mesh, bakes, causes, scene and four views are the finishing test's. All of P's values are data in `finish.json` → `painted`.

**How P paints:**
- Each material is one value.
- Broad washes carry the light and the water.
- A few shapes with a hierarchy carry the damage. Their edges are broken by authored strokes up close and soften with distance.
- Up close, long soft strokes along the boards let each plane breathe.

**Sheets:**
- `look1-*`: pass 1.
- `look2-street.png`, `look2-eye.jpg`: pass 2.
- `look2-boarding.png`: the boarding A/B at the street stop.
- `plan.png`, `plan-big.png`: the value plan.
- `eye.jpg`, `street.png`, `raised.png`, `high.png`: the four views, each beside 09 and 01. In each, the top row is overcast and the bottom row low sun.

**Build:**
1. `run/build.sh`, which now ends with `paint.py`.
2. `run/render.sh p2 eye,street,raised,high P`, under the Unity lock.
3. `run/sheets.sh p2 P`, with the sheets moved here.

For the A/B: `paint.py --boarding a`, then `render.sh p2a street P`.

## Verdict, bad first

1. **The marks are quiet at the street stop.**
   - Bare wood is 52 against paint at 69 to 78. At a glance the corner reads as an old white house, boarded, with failing paint at the foot and under the sill.
   - "Empty for three winters" rests on the boarding and on the one big zone. A cold reader may still find it too clean.
2. **The roof's rolls still show in low sun.** In overcast the roof is one dark mass with a few lit tiles. In low sun, at 18°, every roll's crest still catches the light, though far less than in look 1.
3. **The foot is lighter than planned:** paint at the foot is 69, against 64 in the plan.
4. **The lap shadows break into short dashes in low sun.** This is way A's own known fault, unchanged here.

**What works:**
- **The gable and the street wall separate in overcast,** as the plan asks: 69 against 78. This comes from P's own light, described under Decisions.
- **The wall carries the light:**
  - lighter under a soft contact band at the eave, falling to the foot;
  - a wash widening under the sill;
  - one broad tapering wash from the leaking horn, found on its outer side and lost on its inner side.
- **The marks have a hierarchy:**
  - one big zone at the foot on the leaking side, three courses, each board's patch reaching its lap;
  - one medium on the board under the sill's leaking end;
  - a few small ones (under the dry horn, under the two drips that carry most, and at the gable's foot);
  - the corner board's foot, the casing's leaking leg and the ledge tops.
- **The boarding reads as boarded.**
- **The plinth's wet margin follows the broad splash,** so the scallops are gone.
- **Up close,** the board strokes are visible. By the street stop they are gone.

## Decisions

- **Boarding: b.**
  - The sheet is a weathered mid-grey (52). A damp strip runs down its leaking side (32), with one found, wobbly edge; its other edges are the sheet's own, under the casing.
  - A soft wash darkens the sheet at the head, above the lower batten and at the sill.
  - The battens are lighter (63), so they cross the sheet clearly.
  - a, the dark sheet of look 1, reads as a dark barred window.
- **Exposure: 0.58, for P only.** The sky stays at 71.
- **P's own overcast:**
  - a soft sky from the street: azimuth (-0.15, -1), elevation 50, sun 0.51, shadow 0.35;
  - ambient sky 0.54, equator 0.41, ground 0.08.

  Way A's capture and the low sun are unchanged.

## Measured

Rendered L\* at the street stop, overcast, with low sun in brackets:

| Region | Plan | Look 1 | Look 2 |
| --- | --- | --- | --- |
| Wall, middle | 78 | 81 | 78 (88) |
| Gable | 68 | 79 | 69 (54) |
| Paint at the foot | 64 | 70 | 69 (80) |
| Bare wood | about 50 | about 40 | 52 (57) |
| Sheet | about 50 | 36 | 52 (64) |
| Sheet's stain | about 30 | 26 | 32 (45) |
| Battens | above the sheet | 53 | 63 (74) |
| Plinth | 56 | 51 | 50 (63) |
| Plinth's wet margin | | 27 | 26 (42) |
| Roof, median | dark mass | 36 | 30 (31) |
| Sky | 72 | 71 | 71 (70) |

At eye level in overcast, the sheet is 52 and its strip 34.

## Budget

- **Triangles:** 2,731 near and 793 street, unchanged.
- **Textures P reads:**
  - `hist-p`, 1,024² RGBA;
  - `paint-stroke`, 1,024² RGBA over 1 m;
  - the shared geometry and street-normal pages.

**A still reproduces:** `hist-a.png` and `geo.png` are byte-identical after rebuilding.
