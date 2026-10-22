# Port step 2b: the gully's stone redrawn, its design and "done"

Written 22 October 2026, before any geometry, from the craft study (`docs/research/stone.md`, How stone is built and laid; its notes beside this file). A fresh reviewer's pre-mortem (`premortem.md`) found six ways it would fail; this version answers it (The pre-mortem, answered, at the end). Its decisions are in `docs/stone.md`'s In short (SN1 to SN10).

## The question

Can the gully's stairs and cheek walls, redrawn as rigid stones laid by a mason's rules, hold up beside the target frame (`reviews/lt1/heart/target/3-street-gully-steps-target.png`) at every judging view, read as calm as the clay around them, show no fault of making, and cost a sixth of today's triangles within a frame-time budget?

## Why start again (Q14)

Every one of Q14's four conditions holds:
- **How it is made:** stones sheared along the rake (three places), wall faces built from wobbly outlines, joints left open as slots.
- **Over budget:** 962,000 triangles against a frame of 2 million.
- **Rounds without converging:** eight rounds, then a rebuild.
- **A basic rule broken:** rocks bend (BB3).

Øystein, 22 October: "very buggy and not nice"; "a bit much"; "poorly made. loose lines etc".

**Kept:**
- the kind and its seven stages (`kinds/stair.json`, `stair_stages.py`, `tools/run_kind.py`);
- the record and its facts (`fixtures/records/st-gully.json`): flights, rises, goings, rests, the builder's year, keepers, care and works;
- the plan's set-out;
- the life stage (`upkeep.py`), and the wear and growth laws (`wear.py`, `growth.py`, `water.py`);
- the hash spec and its stable ids;
- the sidecar, the export and installer, the mesh hashes, and the golden and perf tools.

**Redrawn:**
- the parts (`slab.py`, `wallstone.py`);
- the geometry stage's laying, and `wall.py`'s courses, copings and heads;
- the bake's fields where they make marks;
- `Stone.shader`'s marks and its specular filtering;
- new: the face patches (SN6), and an L1 for every part (SN8).

## Decisions

**SN1 Rigid stones** (BB3). Every stone is a rigid convex block cut by planes. It is made by its part function in its own frame, then placed only by a move and a turn. A part's inputs are facts:
- its size from the plan;
- its working (split, pitched);
- its wear, as the hollow and the rounded nosing that feet took off its top, as a field the part subtracts.

Nothing changes a vertex after the part has made it. Joint soil and moss may follow the ground.
- Export check: each placed piece against its part's mesh by best rigid fit; over 0.1 mm fails.

**SN2 Level beds.** Every bed is level, along the wall and across it. The batter, about one in six, is in the face alone: each stone's face is a plane cut at the batter, and its beds stay level (the pre-mortem's story 5).
- No course follows the pitch. Each course starts on the stepped footing uphill and ends under the coping downhill. Through a rest the field runs on unchanged.
- **Footing.** On the stair side it is the steps themselves: the step ends tail 150 mm into the wall and are drawn on the elevation as occupied cells, and the wall is built on them. The course lines are taken from the step tops: one line on each step top, and at most one line between two step tops, so every course meets the stair on a step's top or against a step end's side, never in a wedge, and no stone is under 50 mm high. On the bank side the footing steps with the ground, each step a whole course.
- **Panels.** A wall is laid by panel, between its features (heads, rests, the 1961 panel's edges), each panel on its own id and seed. A record event re-lays its panel and no other.
- **The top** is whole courses, by the wall's role, as the town's own dry lane walls are built. In the twenty local photographs no dry wall beside a flight has a raked coping (`docs/references/stone/`, 29, 32, 33 and 36 to 40); raked copings appear only on dressed granite (42), rendered work and cast kerbs.
  - **A retaining wall** whose bank stands at or over its top has no coping. Its top course is level stones, the bank's turf and plants run over them, and its top line steps with the bank, a whole course a step (32, 36, 38).
  - **A parapet** has level slab copings that step down square at a joint, a whole course a step, as dry wallers set slab copes on a slope (BTCV). A step falls only on a step top's course line, so every coping lies on whole courses. Whether a level run spans one going or two is chosen in grey form at R2b, by how the stepped top reads; an extra course goes in where a step would grow too big (BTCV). Over a rest the coping runs level and drops square at the next flight (29).
  - No stone is cut to a rake, so the gully has no rake cuts, kneelers or knee stones, and the notch at the rest (open fault 2) cannot form. The kneeler stays the rule for a raked coping on dressed work (Rivington Part I, 1904, p. 54; Mitchell 1902; 42's foot block), which the gully's walls are not.
- **Wall ends** are heads of the biggest stones, ties and runners alternating, with a square topstone (fault 4's loose fan goes).

**SN3 Steps.** Block steps of split slate, as the record says. In the town's dry lanes most treads are slabs on laid risers (32, 36, 38, 39, 41), and block steps belong to its formal flights (28, 29, 35, 42); the record decides.
- **Across:** one or two stones a step, never three, never pieced in depth. A joint falls outside the walking line's middle third, alternating sides, and no joint lies within 150 mm of the joint on the step below (no running joint).
- **Lap:** each step's front bears on the back of the one below, lapping 40 to 60 mm.
- **Ends:** both ends go 150 mm into the walls.
- **Rests** keep the plan's form: two to four large slabs, joggled, or setts in a kerb where the plan has setts.
- The 1952 reset run stays a fact: bedded in cement, joints struck.

**SN4 Form.** A stone is drawn as a mason leaves it, with few, large, planar marks.
- **Every line is an edge of the form** (Øystein, 22 October: the loose lines were also "floating lines, disconnected from the shape"). A line on screen is an arris, a joint between two stones, or the boundary of a mark a fact puts there. It starts and ends at another edge, never in the middle of a face. No texture, shader term or strip piece draws a line of its own.
- **The face outline:** four to seven straight edges; no per-vertex noise anywhere. Most stones have no knocked corner. Chips, each a planar cut, go on the corners of the mass (heads, the coping's steps, coping ends, the open ends of steps) and where a fact puts them, as on The Witness's final wall (`research-studios-stylised.md`).
- **Beds and arrises:** beds flat, arrises square.
- **Chamfers:** every exposed arris has a chamfer of 10 to 12 mm, at least 2 px at 8 m through the 28 mm lens, where L0 hands over to L1 (SN8). The nosing's rounding is wear, from the facts.
- **A split face:** at most three planar facets, stepped at least 15 mm where laminae broke. Finer relief lives in the grain map.
- **The tread's top:** a grid only where the wear field varies, at most 120 mm apart across the walking line; flat elsewhere.
- **Hidden faces** (backs, beds, ends inside the wall) are deleted.

**SN5 Joints are filled.** Every joint has a fill no deeper than the joint is wide:
- soil and moss in dry work;
- mortar in the 1952 run and the 1961 panel.

Widths are 4 to 12 mm in the walls and 4 to 10 mm between tread stones. A joint reads as a step in value, never a dark outline. In grey light its fill is within about 6 L* of the faces beside it, and no light rim rings a stone: the two faults The Witness removed from its own wall (its slides 30 and 31; numbers measured on the slides, so they are starting values that R2a and R3 calibrate). No open gap under 2 px at the nearest view (fault: black slots).
- **A wall's fill is one surface per panel**, a plane behind the faces at the joint depth, inclined at the batter: a few large triangles, not a strip per joint. The stones stand proud of it and the joints show it. Joints between tread stones fill to the bed below.

**SN6 Detail from shared sculpted faces** (the craft study's In short 6). Each working (the split face, the dressed top, the coping's top) has a texture array of face patches made once: four split-face patches and two tops to start. Each patch is about 0.5 m at 1 mm a texel, with height, normal and one value channel. Each stone picks a patch, an offset and a turn by its seed, in metric UVs. The tiled grain map leaves the stone's faces.
- **Made by rule, not by hand.** Phyllite splits along its foliation, so a patch is laminae: a few terraces stepped 2 to 15 mm along the cleavage, plucked ledges, and a fine planar tooth within each lamina. Each patch is made in Blender from these rules, baked to its maps and judged alone at 1 m.
- **Faded by footprint** (`OS_Near`): relief and value are true up close and merge to the face's one value before they fall under 2 px.
- **Specular filtering:** Stone.shader calls Unity's `GeometricNormalFiltering` (Tokuyoshi and Kaplanyan) on the patch normal, against the one-pixel lines and specks.

**SN7 Restraint.** One value per stone face, its hue within the stone's range, and at most one accent where a fact puts it. The walking surface is the calmest part. Starting numbers, from The Witness's final wall (unverified, calibrated at R2a and R3): in grey light a face holds within about 2 L*, and neighbouring stones are 1 to 6 L* apart. Detail is medium frequency; edges are drawn by light on the lit arris, never by a dark line beneath it. Three marks are drawn in 2b, and every other mark the shader and the bake make is cut, its fact kept:

| Mark | In 2b | Where it returns |
| --- | --- | --- |
| the face patch (relief and its one value) | drawn | |
| wear and polish: the hollow and nosing in the mesh, polish one low-frequency field along the walking line | drawn | |
| the joints' fill and moss: in the joints and a soft line at the back of each tread, more on the shaded side; mortar a flat fill in the 1952 run and the 1961 panel | drawn | |
| wet (weather, from the shared `Water.hlsl`) | drawn, as state | |
| per-piece hue bins (four) | cut: one value and hue per face instead | |
| rust spots (noise at 9× and 47× a metre) | cut | if the board's phyllite shows rust at the views, as one patch's value |
| lichen discs and their crust relief | cut | in the ensemble, once an A/B at the views shows it reads quiet against busy steps; patches at least a quarter of the face's short side |
| run-off streaks and film | cut | with the ensemble's water, from traced run-off |
| the cement's sand, film, crazing, crumb and lost pointing | cut | never as specks; a repair's age reads by its value |

- **Fading:** every procedural mark is band-limited by its footprint and fades to its mean before it falls under 2 px, smallest first. Courses and silhouettes never fade.

**SN8 Budgets, enforced.**

**Two levels from the start.** Each part function makes L0 and L1 from the same seed and outline, as `docs/building-blocks.md` decides for fitted parts; the port's step 5 builds the chunks and the switching for the town. In 2b:
- **L0** out to about 8 m: the chamfers in the mesh.
- **L1** beyond: the chamfers leave the mesh, and their lit line is kept in the shading by the edge-distance channel; the fills stay. Its geometric error is about 6 mm, above the table's provisional 4 mm. R2a's A/B at 8, 10 and 12 m decides the switch, and the table is corrected with the evidence.
- **Shadows** are cast by L1 at every distance; L0 casts none (`ShadowsOnly`).
- In the experiment's scene a plain LOD group switches them.

Triangles. The export fails above:

| Piece | L0 | L1 |
| --- | --- | --- |
| wall face stone | 40 | 16 |
| coping, head, through | 120 | 48 |
| step stone, rest slab | 300 | 120 |
| sett | 24 | 12 |
| a panel's fill | 8 | 8 |
| **walls** | 110,000 | 45,000 |
| **stairs** | 40,000 | 16,000 |
| **the gully** | 150,000 | 65,000 |

Estimate at L0: about 2,700 wall stones at about 32 triangles over about 140 m² of face, plus 150 copings, comes to about 100,000; 78 steps of about 1.6 stones at 250 to about 31,000; the rests about 8,000.

**Thin triangles,** what the M4 pays for under 4× MSAA (the craft study's In short 7). At each level's far edge (L0 at 8 m, L1 at 20 m), triangles whose smallest altitude is under 2 px are at most 10% of the level's front-facing triangles, the fills included. The median visible triangle is at least 10 px. The contact sheets print both.

**Frame time** at the judging views on the M4, 1440p (Q12), is the A/B of the gully drawn against the gully hidden, offscreen. It is provisional until R0 measures today's gully:

| View | Drizzle and blue hour |
| --- | --- |
| eye-foot, eye-on | 2.0 ms |
| street | 1.2 ms |
| into12 | 1.0 ms |
| high | 0.8 ms |

Low sun is measured and reported. Until 1c's beams it is not gated.

**SN9 Clean making, checked by machine** (the export's checks stage):
- **rigidity** (SN1);
- **contact:** rays from each bed to the stone or ground below; a gap over 3 mm on 30% of a bed fails;
- **overlap:** a BVH pair test, interpenetration over 1 mm fails;
- **welds and T-junctions** on each piece;
- **slivers:** a face under 50 mm or 25°;
- **joint depth** greater than width;
- **open ends:** every wall end is a head; every run of coping ends at a head or a square step onto the run below;
- **no rake:** no stone or coping is cut to a slope;
- **chamfer width** under 2 px at 8 m through the 28 mm lens;
- **floating lines** (SN4), on the golden frames at native size. Lines found by a top-hat in both polarities, over 10 px long, are compared with the mesh's own edges, from a render of piece ids and normals. Any line more than 2 px from an edge fails; none is allowed.

**SN10 Bond is a number.**
- No vertical joint within a lap of 0.4 of the course height (at least 40 mm) of one in the course below.
- No four-stone cross.
- No vertical joint through more than two courses.
- No stone longer than 4.5 times its height; the largest courses low.
- The line of minimum trace is reported per wall panel.

## Done

The redraw is done when all of these hold, the numbers first and the eyes last:
1. **Rigid:** every piece passes SN1's check.
2. **Laid true:**
   - every course is level; every course ends at a footing or the coping;
   - every wall's top is whole courses: a level coping stepped square, or the bank over a level top course; no stone is cut to a rake;
   - every step laps its neighbour and goes into both walls;
   - SN10's bond tests pass.
3. **In budget:** SN8's triangle and thin-triangle gates pass at export for both levels, and its frame-time A/B passes at every view in drizzle and at the blue hour.
4. **Clean:** SN9's checks pass. On the golden frames, at native size:
   - one-pixel lines (a white top-hat, long pieces over 10 px) fall by at least 90% from the baseline and are none on nosings;
   - specks are none;
   - floating lines (SN9) are none;
   - the joints' 5th percentile of L* sits above the darkest cast shadow on open ground, and their median is within 6 L* of the faces beside them in grey light (SN5).
5. **Restrained:**
   - at one-eighth size, the stone's busyness (edge density and high-frequency share of L*) at the street view is within 25% of the target frame's, in the same mask;
   - at eye-foot and eye-on, within 25% of the eye-level target's (R3);
   - at every view, its ratio to the clay beside it is no more than the targets' own stone-to-clay ratio. The measure is calibrated on R0's sheet, on today's gully, the clay and the street target, before any threshold is used;
   - the reviewer reads the eighth-size frames.
6. **The old faults gone,** each confirmed by a check or a native crop:
   - the four open faults: bent courses, the notch at the rest, pillows, the loose fan;
   - the three shared ones: mottled treads, black slots, one-pixel lines;
   - floating lines, disconnected from the shape (Øystein, 22 October).
7. **Facts kept:** every mark that reads as history traces to a record event; two builds hash the same.
8. **Holds at every view:** a strict review on Fable, from native crops at eye-foot, eye-on, street, into12 and high in three lights, beside the street target and the eye-level target, says it holds, and says whether more than the stones must go (Q15).
9. **Proposed, not accepted:** the new golden frames and their sheet go to Øystein, who alone accepts a baseline.

## What would change our minds

- **Repetition seen in the face patches at eye level** (two stones read as one patch): more patches per working, 8 to 16, before adding a single triangle.
- **R0b shows the lines and specks were mostly the pipeline's** (90% gone on today's mesh): the redraw keeps its form decisions, and its clean-making checks move to proving the new mesh adds none.
  Run on 22 October (`r0b/result.md`, `cd79b22`): it did not fire. The pipeline makes none and the stone's named terms 0 to 3%. Growth's colour makes 53% of the lines and 73% of the specks (moss 36% of the lines, lichen 17%), and the mesh alone 48% and 27%, on joints and 1 px nosings. So the redraw owns them all: the mesh's share through SN4's chamfers and SN5's fills, lichen's through SN7, and moss's at R4.
- **The stepped tops read as a sawtooth at the street stop or into12:** longer level runs, with an extra course where a step grows too big (BTCV); never a rake on dry work.
- **The cheek walls turn out dressed or mortared from 1874** (the photographs tie block steps to formal flights, 28 and 42): raked copings on level-bedded ashlar, a kneeler at each foot, and the record changed first.
- **Courses read too coarse beside the board's walls (03, 09, 10):** smaller courses within SN8's gate, which then binds.
- **Over the frame budget with L1 and its shadows:** L1 switches nearer, then the walls' far panels merge into one mesh each.
- **A blind review finding the budgeted stone worse at eye level than today's** (Q13's own reopen).

## The ladder

| Rung | What | Answer it gives | Unity |
| --- | --- | --- | --- |
| R0 | Today's gully A/B, at the five views in drizzle and the blue hour; busyness measured on today's gully, the clay and the street target | the frame budget's base; Done 5's calibration | yes, when the lock is free |
| R0b | Shading only, on today's mesh, one change at a time: the stone's own (`GeometricNormalFiltering`, the joint value floor, the cut marks off) and the pipeline's (bloom with a Karis average, shadow normal bias 0.5 against 0.2, SSAO off), the pipeline's as overrides at render time, never saved; one-pixel lines and specks counted at native size | how much of the lines and specks the redraw owns | yes, in R0's run |
| R1 | Elevations in integer mm: every wall unrolled, by panel, its features first (heads, rests, the coping's steps, the step ends as occupied cells, the 1961 panel's edges, fallen stones), courses filled by choosing; the steps' stones and joints; SN10's tests; a 2D sheet | the layout is a mason's, before any mesh | no |
| R2a | Look-dev: the six face patches, then a wall stone, a step and a coping at L0 and L1, grey first and then in material, in the target's light, at 1, 5 and 12 m, with the patches' two A/B arms on the wall stone (facets ×2, minor ledges off; `r2a/patches.md`, the read of 23 October), which set SN7's number for a split face; the L0 to L1 switch A/B'd at 8, 10 and 12 m, with the town's fog on | the surface model and the levels, on three stones before thousands | yes, to judge |
| R2b | Grey form in Blender: the parts and the laying through the stages, every piece one grey; SN1, SN8 and SN9's checks; a quick sheet at the judging cameras in neutral light | the form and the counts, cheaply | no |
| R3 | Grey form in Unity: the golden views in grey light, native crops, the frame-time A/B; then the eye-level target, painted over the eye-foot and eye-on grey renders with `blender/tools/paintover.py` as the street target was, the clay beside it as it is planned | form at the views, the cost, and the eye level's bar | yes |
| R4 | Materials: the patches, the three marks, the bake's fields made calm (moss among them: its line at the back of each tread is kept soft and band-limited in `Growth.hlsl`, which only the stone uses today; R0b found it today's largest maker of lines), specular filtering; three lights; Done 4 and 5's frame checks | restraint and clean making | yes |
| R5 | The strict review on Fable, from a lean packet: native crops beside both targets, the numbers, this design | the verdict | no |
| R6 | The proposed golden frames and sheet, to Øystein | his acceptance | no |

Each rung passes before the next starts, except that R1, and R2a's patches (made and checked in Blender), run while R0 waits for the lock: neither depends on R0's answers. A rung that will not converge stops: judge the form in grey light, one change at a time.

**Box:** craft and design, about 1 Opus-day. The build, re-sized after the pre-mortem, is about 4 Opus-days: R0 and R0b 0.5, R1 0.4, R2a 0.5, R2b 1.0, R3 0.4, R4 0.5, R5 and R6 0.3, the chores below 0.3. It stops for a re-plan at 6.

**Also in 2b** (`reviews/lt1/port-handover.md`). These stay in 2b for the handover's reason: each changes the hashes and the frames, and the baseline is redrawn now, so doing them later costs Øystein a second acceptance. Most come free, because the redrawn code is written on them from the start:
- the plan in integer mm;
- world seed 1989 (retiring `legacySeed`);
- the eight `--` ids minted;
- slots for the wall heads (SN2 needs them);
- the seed keys renamed;
- `wall.py` adopting `write_export`.

If the box runs over, these are cut first, and the second re-baseline is named in the handover. Then, in order: the 1961 panel's and the 1952 run's own materials (the facts kept, drawn the step after); then the line of minimum trace. R0b, R2a and the eye-level target are never cut. The early cutoff, H1's fields and 2a's leftovers wait for the step after.

## The pre-mortem, answered

`premortem.md` proposed twelve changes. Ten are taken, one in part, and one is answered from the plan.

| # | Change | Answer |
| --- | --- | --- |
| 1 | Shared sculpted face patches are the surface model | Taken: SN6. The craft study chose them; the design had demoted them |
| 2 | R0b, the shading fixes on today's mesh first | Taken: R0b. The pipeline's half is measured by overrides and goes to 1c with the numbers, since bloom, the shadow bias and SSAO are the light's |
| 3 | R2a, three stones in full material before laying | Taken: R2a, with the patches and the levels |
| 4 | An inventory of marks, three kept | Taken: SN7's table. Wet stays, as weather's state |
| 5 | An eye-level target | Taken: R3, made as the street target was |
| 6 | Level beds; the batter in the face | Taken: SN2 |
| 7 | Step ends as occupied cells; a rule for the course above each ledge | Taken: SN2's footing, the course lines from the step tops |
| 8 | L1 at 10 m, a shadow proxy, fills counted, a thin-triangle gate | Taken: SN8. L1 is the shadow proxy; the switch distance is R2a's A/B; the fills became one surface per panel (SN5); the gate is by pixels, not aspect, since a chamfer is thin by nature |
| 9 | Done 5 calibrated | Taken: on R0's sheet, with the eye-level target added |
| 10 | A vertex format decided before R2 | From the plan: the vertex layout is `schemas/channels.json`, and moving history out of the vertices is the port's step 3, a format changed only where a written record fails (`docs/plan.md`, P8). 2b writes through today's bake, kept behind one function for step 3 to replace |
| 11 | "Also in 2b" to its own step | In part: they stay for one re-baseline, are counted in the box, and are the first cut |
| 12 | The box at 4 days | Taken |

The pre-mortem's point on stability under edits is SN2's panels.

## Risks

- **Thin, filled joints may make the walls read as one flat plane at 12 m.** Joints fade there by design, so the courses must hold by value and by the coping's lit line.
- **Spec filtering lives in the shared shading.** If it changes other materials' frames, it belongs to 1c, and the stone keeps its own call.
- **The shadow normal bias (0.5) may cause the orange rims.** That is the pipeline's, not the stone's: R0b measures it, and it goes to 1c with the evidence.
- **Face patches made by rule may read as terraced CG, or as "a bit much."** R2a judges them alone at 1 m against the reference board (`docs/references/stone/`) before any stone is laid, and restraint wins: fewer, larger laminae.
- **L1 without chamfers may pop at the switch.** R2a's A/B at 8, 10 and 12 m, in motion as well as in stills.
- **`wall.py` is still a monolith** with its own build. The redraw writes its laying as functions the wall kind's stages can call later, without making it a kind now.
