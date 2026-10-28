# Painted finish, round 1 (way P)

House 107's corner in 1989, painted as a painter would paint it. The model, mesh, bakes, causes, scene and four views are the finishing test's. All of P's values are data in `finish.json` → `painted`.

**How P paints:**
- Each material is one value.
- The wall carries a big gradient: a contact band under the eave, a light body, and the foot's dirt with a ragged painted top.
- Every junction is dark: under the eave, the sill and each batten, the boards onto the drip board, the plinth under it and onto the ground.
- Three long washes carry the water: from each of the sill's ends, and from the head's leaking end down beside the casing.
- A few shapes with a hierarchy carry the damage. Their edges are torn along the grain and broken by authored strokes up close, with a clean, lighter lip in pieces; they soften with distance.
- Up close, broad dry-brush strokes run along the boards, and drags run down the washes. By the street stop only a trace of them is left.

**Sheets:**
- `look1-*`: pass 1.
- `look2-*`: pass 2. `look2-boarding.png` is the boarding A/B at the street stop.
- `look3-street.png`, `look3-eye.jpg`: pass 3, the final state, beside Hopper, Stålenhag and 09.
- `plan.png`, `plan-big.png`: the value plan.
- `eye.jpg`, `street.png`, `raised.png`, `high.png`: the four views of pass 3, each beside 09 and 01. In each, the top row is overcast and the bottom row low sun.

**Build:**
1. `run/build.sh`, which ends with `paint.py`.
2. `run/render.sh p3 eye,street,raised,high P`, under the Unity lock.
3. `run/sheets.sh p3 P`, with the sheets moved here.

For the A/B: `paint.py --boarding a`, then `render.sh p2a street P`.

## Verdict, bad first

1. **The peeled zones read as stains at the street stop, not as lost paint.**
   - The lighter lip holds only in pieces up close and fades with distance. Without it, bare wood at 50 against foot paint at 62 to 67 reads as damp or dirt.
   - Up close, the torn ends and the lip read as paint failing along the grain.
2. **The foot zone still reads a little as a band across the wall,** above all on the gable, where nothing breaks it. Its top is ragged and it darkens toward the drip board, but a cold reader may take it for a tide line.
3. **The brushwork near is soft blocks along the boards, not a painter's hand.** It has a loaded start and a dry end, at about ±3 to ±5. Beside Stålenhag it is still mechanical: no direction within a stroke, no broken bristle edge.
4. **The upper wall is one clean plane.** Above the sill, only the eave band and the battens' darks carry it. Beside Hopper, the body has no broad modulation of its own.
5. **The washes run straight,** with an even found edge from head to tail. At the street they read as water from the sill. Up close they are a little like vertical bands.
6. **Unchanged from pass 2:**
   - the roof's rolls still catch the low sun;
   - the lap shadows break into dashes in low sun (way A's own fault).

**What works:**
- **The story reads at the street stop at a glance:**
  - two long washes run from the sill's ends, and the leaking one feeds the big failed zone at the foot;
  - the foot is dirty;
  - every junction is dark;
  - the eave band closes the top;
  - the window is boarded.
- **The values land on the plan:** see Measured.
- **It holds from raised and high:** the washes and the failed foot still read, and the junctions are crisp.

## Decisions

- **Junction darks pull toward a value.** Each junction draws the paint down to its own value (`junction.*.to`) rather than subtracting a fixed amount. Where the AO contact, a wash or the boarding's strip is already dark, it adds nothing and never goes to black.
- **The washes have their own page.** `hist-p2` R holds them, and they darken bare wood as fully as paint, since water darkens both. Its strength also places the brush's drags. The washes were invisible in G, where bare wood takes only 30 %, and the big zone lies on their path.
- **The foot's dirt is a stain field** on the boards, so up close the strokes break its edge. Stains now take only `bareShift` of their value on bare wood, so bare wood stays near 50.
- **The rim is the paint's own value plus `rimL`,** not an absolute value. It breaks along its length by the stain strokes' value and keeps 40 % far. As an absolute 96 that held at the street, it outlined every patch like a sticker.
- **G's range is ±80 L\*** (`dlRange`), 0.63 L\* a step, so the junctions fit.
- **The peel's patch ends tear along the grain:** a wave over height, drawing in by 12 cm a metre as they rise. The big zone is wider: 0.55, 0.45 and 0.28 m half-widths.
- **Kept from pass 2:**
  - boarding b;
  - exposure 0.58 for P only, and P's own overcast;
  - the hierarchy of marks;
  - the roof, the lights and the mesh.

## Measured

Rendered L\* at the street stop, overcast, with low sun in brackets. The pass-3 targets are the coordinator's.

| Region | Target | Look 2 | Pass 3 |
| --- | --- | --- | --- |
| Wall, at the eave | about 30 | | 44 (57) |
| Wall, 10 cm under the eave | about 60 | | 59 (39) |
| Wall, 30 cm under the eave | 80 | | 79 (89) |
| Wall, middle | about 80 | 78 (88) | 80 (89) |
| Under the sill | 25 to 35 | | 24 (15) |
| Foot zone, right and left | about 62 | 69 (80) | 62 and 67 (73 and 78) |
| Bare wood | about 48 | 52 (57) | 50 (61) |
| Leak wash, 0.3 m under the sill | −10 to −12 | | −10 (79 → 69) |
| Dry wash, 0.3 m under the sill | −10 to −12 | | −9 (78 → 69) |
| Sheet | 52 | 52 (64) | 52 (64) |
| Sheet's strip | 32 | 32 (45) | 32 (44) |
| Sheet above the lower batten | about −15 | | 34, about −18 (47) |
| Plinth's wet margin | about 30 | 26 (42) | 25 (41) |
| Plinth at the ground | about 15 | | 19 (36) |
| Gable | | 69 (54) | 71 (56) |
| Roof, median | dark mass | 30 (31) | 30 (32) |
| Sky | 72 | 71 (70) | 71 (70) |

The brush near is about ±3 to ±5 at eye level and about ±1 at the street stop.

## Budget

- **Triangles:** 2,731 near and 793 street, unchanged.
- **Textures P reads, each 1,024²:**
  - `hist-p`, RGBA;
  - `hist-p2`, R used, stored RGBA for now, and could be R8;
  - `paint-stroke`, RGBA over 1 m;
  - the shared geometry and street-normal pages.
- **Shader:** one more page read and one more stroke read, which shares the page's sampler.

**A still reproduces:** `hist-a.png` and `geo.png` are byte-identical after rebuilding.
