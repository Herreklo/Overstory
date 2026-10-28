# Painted finish, round p2 (way P)

Step 1 was the critic's change (`../p1/critic.md`): three unequal value planes, and one failed-paint shape that follows the water. Step 2 is the round's list, with the four corrections to step 1. The colour still is the one exception to clay-first.

**Stills:**
- `street.png`, `raised.png`, `high.png`: P in overcast (top) and low sun (bottom), beside photos 09 and 01.
- `eye.jpg`: eye level, in both lights, beside 09.
- `colour-eye.png`: eye level in low sun, clay on the left, colour on the right.
- `step1-*`: step 1, kept for comparison.

## Bad first

1. **At the street stop the wall has lost its clapboard.** Past about 12 m the laps collapse to a few kept lines, which kills the moiré. But 09 and 01, at the same metres a pixel, show every lap as a fine dark line. The next fix: draw the lap lines from the course heights in the shader, anti-aliased at any distance, instead of reading them from the page.
2. **The upper wall is clean** (accepted for this round). Above the sill there is only the eave band, the battens and the window. "Old and empty" comes from the tongue, the ply and the battens.
3. **The peel is small.** The big sliver sits on the course just under the sill, beside the wash's head rather than inside it. At eye level it reads as torn paint with a ragged top, but as one flat lens. The three small ones are flecks. At the street stop the peel is lost in the wash.
4. **In colour, the sun's gold reads as cream paint more than as light.**
   - The lit wall (C 6, h 86) and the wash (C 6, h 81) share a hue, so the wall reads beige.
   - The window's ply (C 7) still leans brown more than grey.
5. **A thin light hairline at one cladding butt joint,** near the lower batten's left end. It dates from q7 and is not fixed.

## What changed in step 2

**Laps, far (`lap.far`).** From 3.5 to 6.5 mm a pixel (about 6.5 to 12 m), the street level keeps only the laps `lap_keep` names. On the rest it:
- flattens the normals;
- opens the baked occlusion, with four taps on `_Geo`.

Each course keeps its own tone (`wall.toneRange`, page 2's A), with its butt's thin contact line moved into it, so the courses still step far off.

**Near brushwork is gone.** The stroke texture is deleted, along with the brush, drag, edge and rim data and their shader terms.

**Peel** (corrections 1 and 2):
- **What it is:** bare silvered timber (`bareL` 50, cool), with a hard `fwidth` edge.
- **The lip** (`lip`): a 3 mm film of paint along each torn edge, lit only where the sun catches it. It scales with the shadow's strength, so it is absent in overcast.
- **The wash** is soft and sits between paint and peel. On bare wood it keeps a tenth (`bareWash`), and the wall's gradient a third (`bareShift`).
- **The slivers:** one large (0.6 × 0.035 m), over the butt joint under the leaking horn, and three small (0.22, 0.16 and 0.12 m). Each runs from its board's butt upward, longer on the side the water spreads to. Its top is torn by smooth noise along the grain, with no steps.

**Battens.**
- They are raw-sawn grey: L 50, matte, grain along their length, end faces lighter (`endL`), rust at the nail heads.
- The dark "peg" at their ends was the batten junction, baked on the cladding behind them. It now falls only on the casing they bear on.
- Their skew and their nails through the trim come from the model, which is unchanged.

**Ply** reads as ply, not as a blind:
- grain along each sheet's long side;
- two oval patches to a sheet;
- darker cut edges;
- nail lines every 150 mm, 20 mm in;
- a damp head band that ends in a slow tide line.

The vertical runs that read as a roller blind are gone.

**Plinth.**
- Granite at L 58, clearly lighter than the roof.
- Darker toward the ground, each block its own step.
- The hard wet-margin stain that made the wavy light stripe is now a soft value.
- Its top, under the drip board, takes 15 less (`capL`).

**Roof.**
- One quiet mass: L 34, with its up faces 12 lighter.
- It keeps 0.3 of the occlusion and contact.
- It looks for its shadow 0.12 m toward the light (`shadowLift`), so its own tiles cast none on it.

**Sun.** Matte: no gloss on the cladding, trims or tiles. The lit white keeps its gradient.

**Colour** (`painted.colour`), hue and chroma only, laid on the clay's L*:
- **Paint:** aged white, warm and greyed.
- **Bare wood and battens:** silvered cool grey.
- **Ply:** grey-brown.
- **Rust:** dull orange-brown.
- **Granite:** cool grey.
- **Pantiles:** dull burnt orange.
- **The light:** low sun, gold on what faces it; the shade and ambient take the sky's blue.

## Measured

Rendered L*, overcast, with low sun in brackets.

**Eye level:**

| Region | L* |
| --- | --- |
| Paint | 63 |
| Wash | 53 |
| Peel | 46 |

So the order is paint, wash, peel, by value as well as by edge.

**Street stop:**

| Region | L* |
| --- | --- |
| Wall, upper | 78 (88) |
| Wall, low | 61 (72) |
| Tongue's core | 45–51 (57–62) |
| Window sheet | 35 (46) |
| Roof | 40 (44) |
| Plinth | 52 (64) |

The tongue is the second dark after the window, one mark from the horn to the plinth.

**Colour still against clay:**

| Region | Colour L* | Clay L* | Colour |
| --- | --- | --- | --- |
| Lit wall | 86.9 | 86.7 | C 5.7, h 86 |
| Shade | 46.6 | 46.4 | C 4.6, h 251: the sky's blue, not magenta |
| Ply | 46.7 | 46.0 | C 7.3, h 73 |
| Battens | 62.8 | 62.1 | C 3.1 |

**Unchanged:**
- the mesh: 2,731 and 793 triangles;
- P's lights, clay and four views.

**The budget is down one texture:** the stroke texture is gone. P samples `hist-p` and `hist-p2` (1024², RGBA) and `geo`. Far street pixels add four taps of `geo`.

**A still reproduces:** `hist-a.png` and `geo.png` are byte-identical.

## Specific to this corner

These are still 107's, and must become facts or general rules before the street:

- **One opening.**
  - The sill, casing and sheets are named features, and the boarding wash reads `battens[0]`.
  - `lap_keep` assumes the opening is on the street wall.
  - `edges()` assumes two walls.
- **The leak side is a seed**, not a fact about the sill's fall.
- **`wear` is calibrated on one house.** The slivers' sizes are 107's, scaled by wear.
- **The ledge tops are cut** at the sample's edge (`meta["sample"]`).
- **The ply's grain follows each sheet's long side.** It should come from the sheet's facts.
- **The era's trims belong to the model and come with the street:** a profiled casing, and a head with a cornice. 09's window has both; ours has plain boards.
