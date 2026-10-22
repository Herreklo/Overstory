# History as a function: the fit (step 3, R1)

Can the stone's per-vertex history today be drawn from a few numbers per texel, per piece and per thing, plus the date? If so, by which law, and at what error once those numbers are 8-bit? This rung gives numbers only. Nothing here touches Unity or the schemas.

**Source.** The gully's stair at a858766 (`stone.py`, `upkeep.py`), in a frozen copy. Both the plain and the instrumented copy hash `bff7858b698f3efd` (354,126 triangles). The instrumentation only names two expressions and appends to a trace.

**Commands** (`B` is `/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python blender/tools/history_fit.py --`):

    git archive a858766 blender | tar -x -C <scratch>/frozen
    $B prepare <scratch>/frozen
    $B prove   <scratch>/frozen <scratch>/out      # PROVE bff7858b698f3efd OK
    $B collect <scratch>/frozen <scratch>/cache    # 67 s: five builds traced, four cuts re-run
    $B fit     <scratch>/frozen <scratch>/cache reviews/lt1/history/fit.md   # writes the numbers below

## In short

- **D5.1's rate-only law does not hold for polish or moss.** A layer that saturates below 1 cannot be a rate: `C(r·t)` goes to `C(∞)` for every `r > 0`. With one rate per texel fitted to 1989, it misses the 1953 build by 70/255 (polish) and 79/255 (moss), on the vertices where the amplitude law misses by 3.9/255 and 1.4/255. Run forward to 2049, it misses by 82/255 and 111/255.
- **The smallest law that fits is Gu's amplitude times a curve, with no per-texel offset.** Polish and moss take an amplitude per texel; lichen keeps a rate per texel. Each layer's clock is one of the piece's clocks, chosen per texel by a reach. At 1989 the law is exact in float. In 8 bits the maximum error is 0.50/255 for polish, 0.26/255 for lichen and 0.50/255 for moss, all under the 1/255 target. At every earlier build the law is exact (0.000) when it reads that build's own fields.
- **The old code's fields are not constants between events.** It computes them on the settled stone, so a slab with no event since 1953 still moves under them. 1989's page, read at 1953, misses by more than 2/255 on 6.4% of the vertices kept in the comparison, mostly at the foot of the steps' fronts (up to 80/255). Proposal: bake the fields on each piece as laid.
- **Prefix:** there are 2, 20, 16 and 3 mismatches at the 1900, 1930, 1960 and 1975 cuts. All of them fall in the cut's own last partial decade. Drawing every decade whole fixes it, with 0 mismatches at every cut and going forward. The fix moves 2 of today's events (both in 1986), so it changes the baseline hash.

## (a) What Stone.shader reads, and where it goes

| Today | Quantity | Source in `put()` | New home | Fit (b) |
| --- | --- | --- | --- | --- |
| UV1.x | years bare / 200 (weathering, grime) | `bare_y / 200` | the piece table's bare year (placed − age brought) and the date | exact |
| UV1.y | variation | `rng.random()` per piece | piece table, u16 | 7.7e-6 |
| UV2.x | face kind | `piece["kind"]` | uv4.x face-kind (as in `channels.json`) | exact |
| UV2.y | water, where it lies and runs | `WT.on_top(back, joint, hollow)` on treads; run-over and constants elsewhere | **P0.G as static water**, plus the hollow term `min(r·A_P·(t−P)/4 mm, 1)` on walked treads | 0.57/255 |
| UV3.x, y | sky seen, ground seen | constants and ramps by kind | P0.B, P0.A | 0.50/255 |
| UV4.x | polish | `WR.polish(footfall, worn_y, foot)`, max with `polish0` | H1.R amplitude; the thing's speed; the piece's placed year; the inherited floor in the piece table | 0.50/255 |
| UV4.y | lichen | `GR.lichen_years(lich_y, ltr, exposed)` | H1.G rate; the piece's bare year, or its disturbed year at the hands' reach; the delay in the material's curve | 0.26/255 |
| UV5.x | moss | `GR.moss(damp·care, mtr, moss_y)` | H1.B amplitude at the bake's care; the clock is bare, or the bed's where H1.A says | 0.50/255 |
| UV5.y | water held | `clip((worn − 3 mm)/3 mm)` on walked treads | **no channel:** the dish's depth `r·A_P·(t−P)`, with H1.R, the thing's wear rate and the placed year | 0.77/255 |

**Water.** The stone reads two water channels; P0 has one, `water-held`. The held water follows the hollow, which deepens with the date, so it is not a place quantity at all. P0.G becomes the static water (the back strip, the joints, a front's run-over). OS_History adds the hollow and the standing water from H1.R and the clock.

**The hollow.** A walked tread's share of the wear rate is the same `foot` that sets its polish amplitude. On a piece feet do not walk on, `worn_y` is 0. So the dish needs no vertex channel: the gully needs nothing in uv4.y's `hollow-rate`.

**The hands' reach** (lichen torn on a lift) is computed in the shader from the face kind and the edge distance, already in uv4.x and uv3.y: a tread within 6 cm of its edge, a nosing, or a front, on a piece flagged as lifted. Every quantity has a home.

<!-- fit:tables -->
Stair: 183,570 vertices in 772 pieces (both flights). Clocks: placed, bare, disturbed (bed and lifted) per piece; polish speed 0.125 a year (footfall 50,000 / 400,000); the keeper's care in 1988 0.25.

**(a) The resets, checked.** Lichen's clock from the piece's bare and disturbed years by the hands' reach (face kind and edge distance): 183,570 of 183,570 vertices exact. Moss's from the bed reach: 183,570 of 183,570 exact. Lifted equals disturbed on every lifted piece: yes. Vertices whose lichen runs from the lift: 30,042; whose moss runs from the bed's relaying (reach 1, disturbed after bare): 5,378. Reclaimed slabs in the gully: 0.

**(b) The page model at 1989 against today's per-vertex values** (every vertex; errors in 255ths; today as the FBX carries it, float32):

| Layer (channel today) | float inputs: max | 99.9th | 8-bit inputs: max | 99.9th | target float / 8-bit |
| --- | --- | --- | --- | --- | --- |
| polish (UV4.x) | 0.00 | 0.00 | 0.50 | 0.50 | 1 / 2 |
| lichen (UV4.y) | 0.00 | 0.00 | 0.26 | 0.26 | 1 / 2 |
| moss (UV5.x) | 0.00 | 0.00 | 0.50 | 0.50 | 1 / 2 |
| held (UV5.y) | 0.00 | 0.00 | 0.77 | 0.74 | (not targeted) |
| water (UV2.y) | 0.00 | 0.00 | 0.57 | 0.57 | (not targeted) |
| years (UV1.x) | 0.00 | 0.00 | 0.00 | 0.00 | (not targeted) |

Variation (UV1.y) in 16 bits: max error 7.65e-06 (half precision, as the shader reads it, rounds at 2.4e-4 to 4.9e-4); in 8 bits 1.96e-03. Sky and ground seen (UV3) in 8 bits: max 0.50 and 0.50.

**(c) Against the frozen code built at an earlier year,** on the pieces unchanged since (no event on their slot or step from that year on, the same clocks, and the year's own life agreeing with 1989's before it). Errors in 255ths, max / 99.9th, polish, lichen, moss:

| Build (care) | pieces kept (vertices) | the law, the build's own fields | 1989's page at that date, float | same, 8-bit | moss with 1989's care, float | D5.1 rate only, polish and moss |
| --- | --- | --- | --- | --- | --- | --- |
| 1953 (0.45) | 605 of 772 (149,533) | 0.00, 0.00, 0.00 | 3.86 / 2.60, 1.36 / 0.36, 164.72 / 57.37 | 4.29 / 2.67, 1.32 / 0.38, 165.00 / 57.06 | 195.13 / 76.29 | 70.24 / 63.13, 135.10 / 62.85 |
| 1964 (0.45) | 686 of 772 (165,196) | 0.00, 0.00, 0.00 | 2.99 / 2.00, 1.22 / 0.30, 164.72 / 48.47 | 3.42 / 2.06, 1.23 / 0.34, 165.00 / 48.39 | 195.13 / 65.02 | 59.71 / 49.59, 135.10 / 49.08 |
| 1966 (0.25) | 686 of 772 (165,196) | 0.00, 0.00, 0.00 | 2.36 / 1.33, 0.99 / 0.20, 195.13 / 40.90 | 2.76 / 1.45, 1.04 / 0.27, 195.00 / 40.86 | 195.13 / 40.90 | 55.08 / 44.82, 160.04 / 53.78 |
| 1975 (0.25) | 708 of 772 (170,019) | 0.00, 0.00, 0.00 | 1.44 / 0.80, 0.67 / 0.13, 97.67 / 25.09 | 1.85 / 0.94, 0.79 / 0.23, 97.75 / 25.18 | 97.67 / 25.09 | 35.31 / 31.89, 97.67 / 45.63 |

Where 1989's page misses an earlier build by more than 2/255 (any of the three layers), by cause:

| Build | vertices over 2/255 (of kept) | a mask crossed (back, joint, bed reach) | a front's foot band (its moss error, max / 99.9th) | elsewhere | the rest (no mask crossed, no band), the amplitude law: polish, lichen, moss | the rest, D5.1 rate only: polish, moss | the inputs' largest drift: polish amplitude, lichen rate, moss amplitude |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1953 | 9,560 of 149,533 (6.4%) | 58 | 9,170 (79.55 / 65.04) | 332 | 3.86 / 2.74, 1.36 / 0.58, 1.41 / 0.41 | 70.24 / 68.83, 79.07 / 64.80 | 3.89, 4.37, 254.79 |
| 1964 | 10,687 of 165,196 (6.5%) | 59 | 10,463 (62.18 / 52.90) | 165 | 2.99 / 2.18, 1.22 / 0.50, 1.17 / 0.38 | 59.71 / 58.90, 54.95 / 50.53 | 3.01, 3.37, 254.80 |
| 1966 | 9,543 of 165,196 (5.8%) | 41 | 9,477 (54.49 / 45.45) | 25 | 2.36 / 1.56, 0.99 / 0.36, 0.70 / 0.27 | 55.08 / 54.17, 53.90 / 53.88 | 2.38, 2.67, 254.80 |
| 1975 | 8,619 of 170,019 (5.1%) | 25 | 8,594 (31.71 / 27.29) | 0 | 1.44 / 0.94, 0.67 / 0.23, 0.67 / 0.19 | 35.31 / 33.45, 45.74 / 45.71 | 1.45, 1.62, 254.80 |

Pieces left out of each comparison (events on them from that year on; their slot's life differing in the build's own last decade; clocks; not in that build): 1953: 8, 50, 0, 109; 1964: 16, 0, 0, 70; 1966: 12, 8, 0, 66; 1975: 9, 4, 0, 51.

D5.1's rate-only law run forward to 2049 (rates fitted to 1989 exactly), against the same code's law on today's fields: polish 82.33 / 52.40, moss 110.86 / 105.82; lichen is the same law in both (its curve is linear until full).

The old code's own jumps (listed, not failed). 1964 to 1966 builds, care 0.45 to 0.25 from 1965, on the 165,196 vertices unchanged since 1964: two years' growth, the care change and the settling it scales (255ths, max and mean):

- polish: 28.53, 0.03
- lichen: 2.71, 1.28
- moss: 171.11, 6.83
- 1946, care 0.30 to 0.45: on the 174,724 vertices whose moss was full by then, the moss amplitude falls by up to 30.55 (mean 4.77). A rising curve from a reset cannot fall, so the interval model must let moss decline there or jump (R6).
- Care as a per-mille scale on 1989's moss amplitude (care 0.25) instead of a rebake, max / 99.9th: care 0.3: 9.93 / 9.92, over 1/255 on 3,089 vertices; care 0.45: 39.39 / 33.25, over 1/255 on 3,067 vertices; care 0.5: 49.24 / 31.74, over 1/255 on 3,056 vertices.

Reclaimed slabs (inherited polish 0.3, age brought 15 to 40 years), pieces with an inherited polish and reclaim events: 1989 0 and 0, 1953 0 and 0, 1964 0 and 0, 1966 0 and 0, 1975 0 and 0.

**(d) Prefix: life at a cut against life at 1989 cut there** (events before the cut: kind, slot or fill, year, details):

| Cut | events before it in 1989's life | mismatches | in the cut's own last decade | by kind |
| --- | --- | --- | --- | --- |
| 1900 | 15 | 2 | 2 (decade 1894 to 1903) | corner 1, crack 1 |
| 1930 | 81 | 20 | 20 (decade 1924 to 1933) | corner 7, crack 10, fix-corner 3 |
| 1960 | 173 | 16 | 16 (decade 1954 to 1963) | corner 2, crack 11, fix-corner 3 |
| 1975 | 185 | 3 | 3 (decade 1974 to 1983) | crack 3 |

The fix (fit.md, (d)), run: the loop reimplemented without it matches the frozen code at 1989 and every cut (0 events and 0 lives differ). With it: the prefix at the cuts, 1900 0, 1930 0, 1960 0, 1975 0 mismatches; 1989 against 2009 cut at 1989, 0. What it moves in today's 1989: 2 events (in 1986), 2 of 78 steps' lives; so the fix changes today's hash.
<!-- /fit:tables -->

## Reading the numbers

**(b)** The law reproduces 1989 exactly in float. The 8-bit error comes only from rounding the inputs. Lichen's error grows with age, as 0.5/255 × (age − 12)/200, and stays under 1/255 for 412 years. A rate-only law can always meet a single date, so 1989 alone cannot reject D5.1. Moving the date in (c) and to 2049 does.

**(c)** With each build's own fields the law is exact, so the law is not where the old code and the page differ. 1989's page read at an earlier date differs for three reasons:

1. **Care.** The old code scales all moss's damp by `1.15 − 0.75·care`, using the care in the year before the build. With 1989's care (0.25), 1953 (care 0.45) is off by up to 195/255. With 1953's own care the miss is still 165/255, and all of that comes from settling (point 2). Care must be part of the moss amplitude. A per-mille scale on 1989's amplitude is wrong by up to 39/255 at care 0.45, because the bake is clipped at 1 on about 3,000 vertices. So **a care change triggers a rebake of H1**, and the page jumps exactly where the old code jumps.
2. **Settling.** Before `put()` measures a block, `settler` sinks it by 0.3 to 1 times `off = (settled + 3 mm)·(1 + 1.5·(1 − care))` and tilts it by up to 1.4°. On the oldest beds, `off` grows from 52 mm in 1953 to 84 mm in 1989. The worst case is the band at a front's foot, where moss is read from the height over the step below on a 4 cm ramp: 31 to 80/255 on 8,600 to 10,500 vertices. Next come the hard masks (the back strip at `along > 0.8`, a joint at `P_y > 0.04`, the bed reach) on 25 to 59 vertices. Last is the walking line's gradient under a tilted slab: polish up to 3.9/255 after 36 years and 1.4/255 after 14.
3. **The pieces.** A slab whose slot's life differs in the build's own last decade is left out of the comparison: 50 pieces at 1953 (the prefix fault, (d)).

So a stone "unchanged since 1953" is not unchanged in the old code: it settles, and its history is re-measured on its new position. Physically, polish and lichen stay on the stone as it sinks and tilts. The proposal is to **compute H1's fields on each piece as laid, in its own frame**, so a texel's value belongs to the stone and settling moves only the mesh; the page then holds exactly between events. Measured on the old code, everything away from the band and the masks drifts by at most 3.9/255 over 36 years of settling, so most of today's look survives. Three costs follow:

- Today's look changes at the fronts' feet. There, moss from a sinking block's foot would need its own clock, or would be dropped.
- Today's look changes along the walking line by a few 255ths.
- Both changes are measured in step 2a, which owns `stone.py`. Øystein judges them.

**Reclaimed stone** never occurs in the gully at any of the five builds. The reclaimed-stock rule (a crack open more than 15 years, then a 35% draw) never fired in the 1952 campaign. The inherited polish and the age brought are therefore taken from the code and are not tested by these numbers.

**(d)** In `upkeep.flight`, the last decade runs from `y0` to `now`. Its odds scale by `(now − y0)/10` and its draws' years by `randint(y0, now − 1)`, so a cut at 1930 draws 1924 to 1929 differently from the 1989 run. All 41 mismatches lie in those partial decades. **The fix, as text:**

- Draw every decade whole: the span, the draws' year ranges and the settling read by the crack odds and the rocking test all run to the decade's end.
- Apply works only before `now`.
- After the loop, drop damage, fixes and shims dated `now` or later. Take the last decade's settling back to `now` unless a work reset the step in it.

`flight_whole` in the tool runs the fix. With the fix off it reproduces the frozen code at 1989 and at every cut (0 events and 0 lives differ). With the fix on, every cut matches, and so does 2009 cut at 1989. It moves 2 events (1986) on 2 of 78 steps, so it should land with step 2a's upkeep refactor and a new baseline. Folding the 1989 log for earlier dates would keep today's hash, but it would break the moment the game runs past 1989.

## (e) The proposal (not in the schemas yet)

**The law.** A layer at date `t` is its amplitude times its material's curve at the thing's speed, from the clock its texel reaches:

| Layer | Value | Per texel | Per piece | Per thing | Material |
| --- | --- | --- | --- | --- | --- |
| polish | `max(A·(1 − e^(−k·min(t−P, 40))), floor)` | H1.R `A` | placed P; inherited floor | `k` = footfall / 400,000 a year | cap 40 years |
| lichen | `clip(q·max(t − c − 12, 0)/200)`, `c` = D at the hands' reach of a lifted piece, else B | H1.G `q` | B, D, lifted | none | delay 12 years, full 200 |
| moss | `A·min((t − c)/60, 1)`, `c` = max(B, D) where H1.A ≥ 0.5, else B | H1.B `A` (care in), H1.A | B, D | none | full 60 years |
| hollow | depth `r·H1.R·(t − P)` on walked treads; held `clip((depth − 3 mm)/3 mm)`; water `max(P0.G, min(depth/4 mm, 1))` | H1.R, P0.G | P, walked | `r` = wear × footfall/1e5 × width / 1e5 m a year | 3, 6, 4 mm |
| years | `(t − B)/200` | none | B | none | none |

**Channels.** H1 is RGBA8 UNorm, linear, scale 1 and bias 0. R is the polish amplitude, which is also the dish's share. G is the lichen rate, as a share of the material's top rate (1/200 a year for slate). B is the moss amplitude at the bake's care. A is the bed reach, 0 or 1, read at 0.5. P0.G is the static water, with the tread's 0.12 floor baked in.

**Resets.** A piece needs placed (P: polish and the dish), bare (B = P − the age it brought: lichen, moss and weathering) and disturbed (D: when the bed was relaid). On every lifted piece in the gully, lifted equals disturbed, so a "lifted by hands" flag takes the place of a fourth year. All of these go in the piece table. H1's rebuild list becomes a reset, a rate change and a care change.

**The amplitude** lives per texel in H1.R and H1.B, never in the interval: care cannot be a scale (39/255, above).

**The age offset.** No texel needs one. Lichen's 12-year delay is the material's. A reclaimed stone's 15 to 40 years are the piece's, held in whole years as u8 (0 to 255), which is what the code draws. h1.a in months at 8 bits holds only ±10 years, so it is freed for the bed reach.

**Schema edits**, as text:

```diff
 maps.json, h1
-  "describes": "history: polish, lichen and moss rates; the age offset",
-  "channels": {"r": "polish", "g": "lichen", "b": "moss", "a": "age-offset"},
-  "rebuild": ["a reset", "a rate change"],
+  "describes": "history: polish amplitude, lichen rate, moss amplitude at the keeper's care; the bed reach. Baked on each piece as laid, in its own frame",
+  "channels": {"r": "polish-amplitude", "g": "lichen-rate", "b": "moss-amplitude", "a": "bed-reach"},
+  "rebuild": ["a reset", "a rate change", "a care change"],
 maps.json, p0
-  "describes": "place: feet, water held, sky seen, ground seen",
-  "channels": {"r": "feet", "g": "water-held", "b": "sky-seen", "a": "ground-seen"},
+  "describes": "place: feet, water where it lies and runs (OS_History adds the hollows' from h1.r and the date), sky seen, ground seen",
+  "channels": {"r": "feet", "g": "water", "b": "sky-seen", "a": "ground-seen"},
 layers.json, describes
-  "A layer's value at a date is its material's curve at rate x (date - reset + age offset): the page holds the rate, the piece table or facts buffer the reset year, h1.a the age offset"
+  "A layer's value at a date is its amplitude times its material's curve at its speed x (date - clock): the page holds the amplitude (polish, moss) or the rate (lichen) and the clock's reach, the piece table the clocks (placed, disturbed, age brought, lifted), the facts buffer the thing's speed"
 layers.json, each of polish, lichen, moss
+  "law": {"form": "amplitude" | "rate", "clock": "placed" | "bare, disturbed at the hands' reach" | "bare, disturbed where h1.a", "curve": ..., "delay": 12 (lichen)}
 layers.json, notLayers
-  {"map": "h1", "channel": "a", "is": "the age offset, in the units of the interval's ageOffsetMonths, ..."}
+  {"map": "h1", "channel": "a", "is": "the bed reach: 0 moss runs from the bare year, 1 from the bed's last disturbance; read at 0.5"}
 interval.schema.json
-  "... its material's curve at rate / 1000 x (date - resetYear + ageOffsetMonths / 12) (decisions D5.1)"
+  "... the texel's amplitude times its material's curve at rate / 1000 x (date - clock); resetYear is the bare or placed year, ageOffsetMonths the age brought (the piece table keeps whole years)"
+  "reach": {"year": <integer>, "by": "hands" | "bed"}   (optional: the disturbance that resets a part of the fill)
 chunk-format.md, section 4
-  piece table | 24 bytes: u64 seed, u32 fill id (string), u16 thing, u16 part, u16 reset year counted from the pack's first year, u8 material class, u8 flags, u32 reserved
+  piece table | 32 bytes: u64 seed, u32 fill id (string), u16 thing, u16 part, u16 placed and u16 disturbed (years counted from the pack's first year), u16 variation, u8 age brought (years), u8 inherited polish (/255), u8 material class, u8 flags (bit 0 walked, 1 lifted by hands, 2 reclaimed), 6 bytes reserved
 channels.json, uv4.y
   hollow-rate: the gully needs none (a walked tread's dish is h1.r times the thing's wear rate); kept reserved
```

**Open for later rungs:**

- BC7 on H1, against the 1/255 target, and on a binary H1.A at a chart's edge (R5).
- Moss falling at a care improvement. 1946 asks the amplitude to drop by up to 31/255 on fully grown moss, which a clock cannot do (R6).
- The fields as laid, and the upkeep fix, both in step 2a.
