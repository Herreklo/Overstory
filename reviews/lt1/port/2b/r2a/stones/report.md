# R2a stones: report

Port step 2b, rung R2a: the gully's three stones redrawn (the step, the wall stone and the coping). Written 23 October 2026 from the builders' files (`blender.md`, `run-log.txt`), `counts.json`, the sheets and the reference board. Every number here was checked against `counts.json` or a sheet, and I say where I disagree with a builder. No reviewer has passed anything here.

## In short

**Asked.** Do the three stones hold SN7's restraint and SN8's budgets at 1, 5 and 12 m? Does L1 pass for L0 at 8, 10 or 12 m? Which split face does the wall stone want: patches as built, facets ×2 or minor ledges off?

**Passed.**
- Every stone is within its triangle budget at both levels, and imports as built.
- Thin triangles hold over the level: 7.3% at L0, 2.2% at L1.
- With their contexts, no open face shows in any view, level or stand.
- The off-state frame is byte-identical against the current shader.
- In grey, the joints sit within about 2 L* of the faces, and no stone has a ring.
- The coping's switch passes everywhere at 12 m.
- `tools/check.py` does not exist yet; the builders' own tests and `tools/validate_record.py` pass.

**Failed.**
- The wall stone's switch pops at every distance tried, all in the joints: switch p99 is over motion p99 by up to 15.6 L* at 8 m and 8.9 at 12 m, in sun.
- The step pops in grey at the sun stand, on the nosing (+3.4 to +4.2).
- In material, the joint soil reads 11 to 28 L* under the faces in three lights of four: a near-black grid.
- SN4's 2 px chamfer fails on the wall stone at 8 m (1 px), because the fill buries it.
- Beside 05 and 10, the wall reads as flat tiles in regular courses, and the step as a plain bar.

**Proposals.**
1. Keep SN7's split face at about 2 L* and the patches as built. Neither arm changes what reads; the flatness is form at block scale.
2. Use one switch rule for every part, light and stand, with a distance per part. For the wall stone, move L1's outline to where L0's stone meets the fill. Replace the 9 mm error with the visible joint error.
3. Move the soil into the pack's data. First find out why its contrast depends on the light, then fix it.

## The numbers

### Parts

| | Step | Wall stone | Coping |
| --- | --- | --- | --- |
| Specimen | `st-gully/fl-0/tr-9/sl-1` | `wl-gully/fl-1/r/pn-4/bank/co-21/sp-1` | `wl-gully/fl-0/r/pn-4/cp-3` |
| L0 triangles (budget) | 144 (300) | 18 (40) | 36 (120) |
| L1 triangles (budget) | 69 (120) | 10 (16) | 26 (48) |
| Vertices as imported, L0 / L1 | 432 / 207 | 54 / 30 | 108 / 78 |
| Thin at L0, 8 m (Blender) | 10 of 137 (7.3%) | 0 of 10 | 2 of 11 (18.2%) |
| Thin at L0, 8 m (Unity) | 12 of 137 (9%) | 0 | 2 |
| Thin at L1, 20 m | 3 of 60 | 0 of 4 | 0 of 5 |
| L1's mesh error from L0 | 8.51 mm | 9.21 mm | 8.98 mm |
| Chamfer on screen at 8 m in context (top / upright) | 3 / 1 px | 1 / 1 px | 3 / 2 px |
| Open faces, every view, level and stand | 0 px | 0 px (alone: 20,886 at 1 m) | 0 px |
| Joint against face, grey | within 2.2 L* | within 2.2 L* | within 2.2 L* |
| Joint against face, material | −11.7 to −16 | sun −28, drizzle −14, low-sun shade −11.4, blue hour −3.6 | bottom joint −35.5 in sun |

The pools: at L0, 8 m, 2,028 of 27,794 front-facing triangles are thin (7.3%: steps 13.7%, wall stones 0%, copings 23.4%). At L1, 20 m, 243 of 11,016 are thin (2.2%). The walls kind's L1 is 0.580 of its L0 (limit 0.6).

SN8's 10% applies to the level. So the coping's 18.2% and the steps' 13.7% pass only because the wall stones carry them. Unity counts two more thin triangles on the step than Blender does, and neither file explains why.

### Levels: switch p99 against motion p99, L* (difference in brackets)

The switch is |L1 at frame k − L0 at frame k−1|. The motion is |L0 at k − L0 at k−1|, in a dolly from 6 to 14 m. The foot stand is in shade. The sun stand faces the low sun of 16:00 (bearing 316, 8° up).

| Part | Stand, light | Look | 8 m | 10 m | 12 m |
| --- | --- | --- | --- | --- | --- |
| Step | foot, drizzle | grey | 2.7 / 2.7 (+0.0) | 2.0 / 1.8 (+0.2) | 1.5 / 0.9 (+0.6) |
| | | material | 2.3 / 1.7 (+0.6) | 2.0 / 1.3 (+0.6) | 1.6 / 0.9 (+0.6) |
| | foot, low sun | grey | 0.8 / 0.6 (+0.2) | 0.7 / 0.6 (+0.0) | 0.6 / 0.4 (+0.2) |
| | | material | 1.9 / 1.6 (+0.3) | 1.6 / 1.3 (+0.3) | 1.9 / 1.0 (+0.9) |
| | foot, blue hour | grey | 2.0 / 1.9 (+0.1) | 2.0 / 1.9 (+0.0) | 1.0 / 0.6 (+0.5) |
| | | material | 2.0 / 0.9 (+1.1) | 1.7 / 0.9 (+0.8) | 1.3 / 0.8 (+0.5) |
| | sun, low sun | grey | 6.2 / 2.8 (**+3.4**) | 5.7 / 2.1 (**+3.5**) | 5.9 / 1.8 (**+4.2**) |
| | | material | 4.5 / 3.5 (+1.0) | 4.5 / 3.2 (+1.4) | 3.6 / 2.2 (+1.4) |
| Wall stone | foot, drizzle | grey | 6.3 / 0.5 (**+5.8**) | 5.1 / 0.5 (**+4.6**) | 4.6 / 0.6 (**+4.0**) |
| | | material | 12.8 / 2.6 (**+10.2**) | 10.2 / 0.4 (**+9.8**) | 8.8 / 0.9 (**+7.9**) |
| | foot, low sun | grey | 1.7 / 0.2 (+1.6) | 1.6 / 0.2 (+1.4) | 1.4 / 0.2 (+1.1) |
| | | material | 7.0 / 0.6 (**+6.4**) | 6.4 / 0.5 (**+5.9**) | 5.4 / 1.4 (**+4.0**) |
| | foot, blue hour | grey | 2.9 / 0.3 (**+2.5**) | 2.5 / 0.3 (**+2.2**) | 2.2 / 0.4 (+1.7) |
| | | material | 3.7 / 0.3 (**+3.3**) | 3.4 / 0.2 (**+3.2**) | 2.8 / 0.8 (+2.0) |
| | sun, low sun | grey | 18.3 / 2.7 (**+15.6**) | 14.1 / 4.0 (**+10.1**) | 12.9 / 4.0 (**+8.9**) |
| | | material | 19.5 / 3.9 (**+15.6**) | 15.4 / 2.3 (**+13.1**) | 12.0 / 5.0 (**+6.9**) |
| Coping | foot, drizzle | grey | 1.9 / 1.2 (+0.7) | 1.2 / 0.4 (+0.8) | 1.0 / 0.4 (+0.6) |
| | | material | 3.3 / 1.1 (**+2.1**) | 2.9 / 0.7 (**+2.1**) | 2.2 / 1.1 (+1.1) |
| | foot, low sun | grey | 0.8 / 0.4 (+0.3) | 0.4 / 0.2 (+0.2) | 0.3 / 0.2 (+0.1) |
| | | material | 1.3 / 0.6 (+0.7) | 1.0 / 0.4 (+0.6) | 0.9 / 0.7 (+0.1) |
| | foot, blue hour | grey | 1.0 / 0.6 (+0.4) | 0.5 / 0.4 (+0.2) | 0.5 / 0.3 (+0.2) |
| | | material | 2.3 / 1.2 (+1.0) | 2.1 / 0.5 (+1.6) | 1.5 / 0.8 (+0.7) |
| | sun, low sun | grey | 4.1 / 3.8 (+0.3) | 3.3 / 2.3 (+1.1) | 2.1 / 1.4 (+0.7) |
| | | material | 4.4 / 3.9 (+0.4) | 3.4 / 1.8 (+1.6) | 3.0 / 1.7 (+1.3) |

Bold is over the rule proposed below (motion + 2 L*).

- The wall stone alone, without its context, is within +0.4 everywhere. It was not run at the sun stand. So the pop is in the joints, which only the context draws.
- The mean level difference along the dolly does not fall with distance: sun 1.53 at 6 m and 1.52 at 13.7 m; foot drizzle in material 1.77 to 2.09.
- Motion p99 is itself noisy: 0.4 to 2.6 at one stand and look.

### Arms: the wall stone's split face, spread (L* p5 to p95) in grey

| Arm | Sun stand, 1 m | Sun stand, 5 m | Foot, low sun, 1 m | Foot, low sun, 5 m | Alone, foot, low sun, 1 m | Alone, 5 m |
| --- | --- | --- | --- | --- | --- | --- |
| As built | 1.68 | 1.00 | 0.57 | 0.28 | 1.86 | 1.40 |
| Facets ×2 | **3.01** | **1.61** | 0.53 | 0.28 | 1.83 | 1.40 |
| Minor off | 1.68 | 1.00 | 0.57 | 0.28 | 1.86 | 1.40 |
| Patch off (flat) | not run | not run | not run | not run | 1.83 | 1.40 |

At the foot in drizzle, as built against flat is 1.35 against 1.35 at 1 m, and 1.62 against 1.62 at 5 m. In blue hour the stone alone spreads 3.65 at 1 m, with the patch and without it.

Spread was measured in grey only. In material, the files hold only each arm's change against as built (mean / p95 of |ΔL*|):
- facets ×2: at most 0.15 / 0.55;
- minor off: at most 0.09 / 0.22.

In grey, facets ×2 changes at most 0.30 / 0.63 (sun stand, 1 m), and minor off at most 0.06 / 0.15. Minor off changes about as much at 12 m as at 1 m. A pure re-render difference would look like that, so it is not proven that the arm reached the shader.

## What the images show

By my own eye, on the sheets and in native crops, beside the references in `docs/references/stone/`: 05 (`05-aksla-old-split-stone-steps.jpg`), 10 (`10-bergen-dry-stone-wall-and-bedrock.jpg`) and 06 (`06-worn-stair-with-lichen-dale-vestland.jpg`).

- **The wall reads as tiles.** Each face is one flat plane, much the same in value, in regular courses, like raised tiles or orange bricks set in dark mortar. In 10, the stones vary in size, outline and value; the courses wander; the joints are irregular dark gaps with stone in them. In 05, each block has large facets, cracks, knocked corners and lichen mottle. The R2a stones match neither. This is form at block scale, not texture, and no arm changes it.
- **Light right, dark left.** At the sun stand each wall stone has a light line on its sun-facing end chamfer (+8.5 L*) and a dark line on its shaded left end (−36 L*). Together they outline every stone like a drawn tile. SN7 says an edge is drawn by light, never by a dark line.
- **The course below** lines its facet steps up into one horizontal line along the wall.
- **The black grid.** In material, the joints read near-black in drizzle, in low-sun shade and in sun. The grey sheets cannot show it, because grey gives the fill and the stone one albedo. So SN5's grey test passes by construction.
- **The switch.** In `sheets/wallstone/levels.png` at 8 m, the joints visibly narrow when L1 comes in, in sun and in drizzle. The wall seems to tighten.
- **The step** is a plain bar, where 06's fronts are cracked, many-planed and lichened. At the sun stand, the nosing's facets and the front and left arrises flicker at the switch in grey. **I disagree with the builder** that the step in its context "adds about 1 L* in sun": that holds in material only. In grey it is +3.4 to +4.2.
- **The coping** has a dark smudge at its left end. In material in sun, L0 shows dark lines of 16 to 64 px on its form edges. Its top reads saturated blue in shade. The builder calls that "the light, not the part", and I agree it is the light, but it still makes the sheet hard to judge.
- **The light itself** gets in the way of judging. Every view at the sun stand is saturated orange, even in grey. Up-facing faces in shade (the coping's top, the step's tread, the chamfers) are saturated blue. The foot is near-black in blue hour (face L* 4) and in low-sun shade (L* 12).

## Proposals

### 1. SN7's number for a split face

**Proposed.** Keep about 2 L* as a starting value, and keep the patches as built. This is the coordinator's lean, and the evidence supports it.

**Evidence.**
- On a split face the patch draws under 1 L* (0.16 mean, 0.6 p95 at 1 m). The spread is the same with the patch and without it (1.35 / 1.35, 1.62 / 1.62, 1.86 / 1.83). The face's spread of 0.3 to 3.7 L* comes from the light across its planes, not from the patches.
- Facets ×2 doubles the spread only in raking sun, close up: 1.68 to 3.01 at 1 m, 1.00 to 1.61 at 5 m. Each pixel moves by −0.8 to +1.1 L*. I cannot tell the arms apart in `sheets/wallstone/arms.png`, or in a native crop at 1 m in sun.
- Minor off is not proven to have taken (see above).
- What fails against 05 and 10 is that each face is one plane, in a stone of one size and value. A patch cannot fix that.

**Not settled.** The A/B cannot set SN7's number, because nothing it varied changes what reads. Also, the split-face patches are close to invisible even before OS_Near's fade: 0.12 to 0.24 mean and 0.33 to 0.6 p95, unfaded. They cost a lookup and a data path for no visible mark. The bed patch draws 0.9 to 2.0 unfaded, and OS_Near takes it to the floor by 2 m. That is a question for R2b, not a change now.

**What would change our mind.** A blind cold reader preferring facets ×2. Or R2b giving the face its block-scale form, after which a 2 L* face reads dead beside 05.

### 2. The L0 to L1 switch

**Proposed rule.** One pass criterion for every part, light and stand, in grey and in material: switch p99 at most motion p99 + 2 L*. The 2 L* is a starting value. Motion p99 is noisy, so the alone control (within +0.4) shows the measure's floor.

**Distances, from the table:**

| Part | Result | Distance |
| --- | --- | --- |
| Coping | Passes everywhere at 12 m. At 8 and 10 m it misses by 0.1 in one case (drizzle, material). | 12 m now; 10 m if it passes after the soil fix |
| Step | Passes at the foot. Fails in grey at the sun stand at every distance, on the nosing. | 8 m, once L1 keeps the nosing's facets. L1 has room: 69 of 120 triangles. |
| Wall stone | Fails at every distance tried. | None until it is fixed |

**The wall stone's cause.** L0's fill lies no deeper than the joint is wide, so it covers most of the 12 mm chamfer. The visible joint at 1 m is then 13.7 to 24.4 mm, wider than SN5's 4 to 12 mm. L1 has no chamfer, so its visible joint is 4.2 to 9.5 mm. At 1 m, L0 to L1:
- top 13.7 to 6.0 mm;
- bottom 16.1 to 9.5 mm;
- left 24.4 to 8.3 mm;
- right 20.2 to 4.2 mm.

The lit line is right: L1's face band reads 41.1 against L0's chamfer at 39.8. What is wrong is the outline.

**The three options:**
1. **L1's outline at the line where L0's stone meets the fill.** I recommend this, with the coordinator. It adds no mark and no triangles. Today's numbers put it at roughly half the difference per side: about 4 mm in at the top and bottom, and about 8 mm at the ends. Set it from the geometry, then re-run the dolly.
2. **The lit line also paints the joint's opening.** This adds a drawn mark, and the mark would have to track the fill's colour in every light. Not recommended.
3. **The switch at about 18 m.** Not supported. The level difference does not fall with distance, and a 16 mm visible error gives about 32 m by the 2,000× rule, not 18.

**First,** settle SN4 against SN5. As built, the fill buries the chamfer to 1 px at 8 m; at 1 m, 5.4 mm of it shows at the top and 3.0 mm at the ends. How far the outline moves depends on how much chamfer is meant to show.

**L1's error figure.** Replace the 9 mm mesh error with the visible joint error, measured in context (today about 16 mm at an end joint). Keep the mesh error as a check. The mesh error said "safe beyond about 18 m" and missed the joints entirely.

**What would change our mind.** If the dolly, re-run with option 1, still pops in material, the soil (proposal 3) is part of the pop and comes first.

### 3. SN5's joint soil

**Proposed.** The soil is a material fact: what a dry joint is filled with and how dark it is. Today it is a code constant, `_Soil = (0.32, 0.30, 0.26)`, in `LT1Stone.cs` line 89, on the slate material only. It belongs in the pack, as `packs/stavanger-1989/materials/soil.json`. `walling.json`'s working would name its fill (dry: soil; the 1952 reset: cement), and `LT1Stone.cs` would read it.

**The diagnosis comes first.** Before light, the stone should be about 2.5 to 2.8 times the soil's luminance (0.50 against 0.32, sRGB). On screen the face is 3.8 times the joint in sun, and about 18 times in shade. So something in the fill's shading darkens it more where the light is soft. The candidates are in the fill branch of `Stone.shader` (kind > 5.5):
- the moss term (`hist.b × 1.3`);
- the wet term;
- the low smoothness (0.12) under a sky-only light;
- occlusion.

**Where:** a short Unity run on the wall stone's context, at the foot and at the sun stand. Read the `-albedo` view for the ratio before light, then turn each term off in turn, against 3.8 and 18.

**Not the fix.** The R0b JointFloor arm clamps the soil to the face's L* − 6. That hides the symptom, and it would make the joint's value a rule instead of a fact.

**What would change our mind.** If the `-albedo` view already shows 18 in shade, the soil's colour is wrong, and the fix is the data value, not the shading.

## Faults

All of them, including those that go to R2b.

**The look**
1. The wall stone's switch pops in the joints at 8 to 12 m (proposal 2).
2. The step's switch pops in grey at the sun stand, on the nosing's facets and the front and left arrises.
3. SN4's 2 px chamfer fails in context at 8 m: the wall stone 1 / 1 px, the step's uprights 1 px. Blender's check (3.56 and 2.52 px) was on the stone alone, and the fill buries the chamfer.
4. SN5 in material: the joints sit 11 to 28 L* under the faces in three lights of four (proposal 3). The coping's bottom joint, at −35.5 in sun, is partly true shadow under its 32 mm overhang.
5. Light rims in grey:
   - the wall stone's top chamfer, +7.6 / +8.9 L* in drizzle (1 / 5 m);
   - the wall stone's sun-facing end, +8.5 / +8.7;
   - the coping's end chamfers, +12.9 in drizzle and +7.6 in blue hour, measured against the face alone (the top was not found beside them).

   None rings a stone, so SN5 passes. The design does not say whether a chamfer counts as a neighbour under SN7's 6 L*.
6. The shaded left end chamfer, at −36 L*, reads as a dark line on every stone at the sun stand.
7. The faces read as tiles against 05 and 10: one plane each, even in size and value, in regular courses (R2b).
8. The course below aligns its facet steps into one line (R2b).
9. The step is a plain bar against 06 (R2b).
10. The coping has a dark smudge at its left end, and dark lines of 16 to 64 px on its form edges in material in sun.
11. Specks: at the sun stand, the wall stone at L1 has 5 at 1 m, against L0's 1.

**The making**

12. The steps' corner caps make 5.7 of their 13.7 thin points. The coping's corner rule was not applied to the step (R2b).
13. The thin share holds over the level, not per kind: steps 13.7%, copings 23.4%. Unity counts the step 12 of 137 thin; Blender counts 10.
14. The walls kind's L1 is 0.580 of L0, near the 0.6 limit.
15. Alone, the wall stone's open band shows (20,886 px at 1 m). Only a neighbour hides it, so the end of a wall or a fallen stone would show it.
16. The wall stone's chamfer is fixed at 12 mm to keep it out of the thin share, so it cannot vary with wear or history.
17. There are four slivers of 0.26 to 0.33 mm.
18. One row carries the wear.
19. No laid step with an open end was tried in context; the variants pass alone.
20. `stones.py` is 3,636 lines.

**The contexts**

21. The face planes' datum is not in data.
22. The step's cheek face lies 22 to 48 mm inside the walking width at `tr-8`.
23. The backs of `cp-2` and `cp-4` miss the bank plane by −110 and +112 mm.
24. The L1 test's 7.5 mm margin and the readback's scaled normal bound are the builder's own choices, named in `blender.md`.
25. The fill grid merges lines under 10 mm.

**The evidence**

26. The off-state proof is one frame (eye-foot, 1600 low sun). It is byte-identical, and it was re-run after the lit line's second form, against the current `Stone.shader` (md5 1656f6c1…).
27. Minor off is not proven to have taken.
28. No spread was measured in material.
29. Motion p99 is a noisy baseline.

**Conflicts in the files** (from `blender.md`, not yet put right):

30. `kinds/stair.json` gives a lap of 100, against walling's 40 to 60.
31. L1's error is 11 mm in the definitions, against 8.5 to 9.2 mm measured.
32. The L2 to L4 errors.
33. SN10 against R1's cell check.
34. `copeThickMm`.

`Pivot()` is fixed, per the run log.

## Data and code

| What | Where | Why there |
| --- | --- | --- |
| The facts the parts are fitted to (joints, laps, courses, wear, history) | `packs/stavanger-1989/` (`walling.json`, `stairs.json`, `materials/slate.json`, `materials/granite.json`, `parts/`); R1's laying (`masonry.lay` at the pinned commit) | The setting is a pack, and a part is a function whose inputs are facts |
| The three parts | `blender/parts/stone/slate/stones.py` (step, wall stone, coping; PARAMS read through `param()`) | Each part is built and judged one at a time |
| The contexts | `blender/parts/stone/slate/context.py` | Each specimen's neighbours within about 0.6 m, built by their own parts |
| The materials' colours | `unity/Assets/Code/Editor/LT1Stone.cs`, as code constants (`_Stone`, `_Fresh`, `_Edge`, `_Soil`, `_Water`) | A saved material keeps its values, so they are set by code, never by shader defaults |
| The fill, the lit line and the off-state | `unity/Assets/Shaders/Stone.shader` (kind 6; UV6 and UV7) | One shader for every stone |
| The near fade | `Detail.hlsl` (`OS_Near`) | Shared by every element |
| The harness and the arms | `unity/Assets/Code/Editor/LT1R2a.cs` (`_OS_PatchShift`) | Experiment code, not the game's |
| The counts | `tools/r2a_count.py`, which writes `counts.json` | Re-runnable from the frames |

**Still to come, as R2a's last piece: the data move.**
- PARAMS go into the part definitions as a `params` object, which opens the closed `part.schema.json`.
- New keys in `walling.json`: `jointMm`, `batterPerHeight`, `topThickMm`, `copeOverMm` and `copeProudMm`.
- A new key in `materials/slate.json`: `cornerBreak`.
- Then the soil goes to the pack (proposal 3).

The colour constants are material facts held as code. The soil is the one that matters now; the others follow once a material file holds colour.

## Follow-ups

- **OS_Near's thresholds have no data home.** The table in `docs/foundations.md` shows "—" for detail by distance.
- **ArtImport's weld.** Unity's FBX import merges corners, so every triangle carries its own three control points. Recorded for R3.
- **The stand lights.** No lamp is near the foot (the nearest is 13 m up the flight), and the three rigs have their lamps off. The plan's "inside a lamp's pool" cannot hold in these rigs.
- **The rigs' light.** The orange sun even in grey, the blue shade on up-facing faces and the near-black foot make the sheets hard to judge. This goes to the light's owner, not to the stones.
- **The file conflicts** above go to the definitions' owner.

## What a reviewer should judge

- Do the wall's stones read as split stone or as tiles, beside 05 and 10?
- Is the switch rule right (motion + 2 L*, every light and stand, grey and material), and are the per-part distances right?
- Does option 1 follow from the cause shown? Should SN4 against SN5 be settled first?
- Does the A/B support keeping 2 L* and the patches as built, or does it only show that it could not decide?
- Is the soil's contrast a data fault or a shading fault? Is the diagnosis named well enough to run?
- Is anything here flattering the work, such as SN5 passing in grey by construction, or the thin share held over the level?
