# Port step 2b: the gully's stone redrawn, its design and "done"

Written 22 October 2026, before any geometry, from the craft study (`docs/research/stone.md`, How stone is built and laid; its notes beside this file). It goes to a fresh reviewer's pre-mortem first, is fixed from it, and only then built. Its decisions join `docs/stone.md`'s In short (SN1 to SN10) once the pre-mortem has been answered.

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
- `Stone.shader`'s marks and its specular filtering.

## Decisions

**SN1 Rigid stones** (BB3). Every stone is a rigid convex block cut by planes. It is made by its part function in its own frame, then placed only by a move and a turn. A part's inputs are facts:
- its size from the plan;
- its working (split, pitched);
- its wear, as the hollow and the rounded nosing that feet took off its top, as a field the part subtracts.

Nothing changes a vertex after the part has made it. Joint soil and moss may follow the ground.
- Export check: each placed piece against its part's mesh by best rigid fit; over 0.1 mm fails.

**SN2 Level beds.** Every wall course is level along the wall. Across it, each stone is square to the battered face, about one in six: a turn, not a shear.
- No course follows the pitch. Each course starts on the stepped footing uphill and ends under the coping downhill. Through a rest the field runs on unchanged.
- **Footing.** On the stair side it is the steps themselves: the step ends tail 150 mm into the wall, and the wall is built on them. On the bank side it steps with the ground, each step a whole course.
- **The coping** is raked over a flight and level over a rest, and is laid on the cut tops of level-bedded stones:
  - a **kneeler** at the foot of every raked run, at the lane and at every rest-to-flight break: a big stone with a level bed, its top cut to take the run;
  - a **knee stone** at every flight-to-rest break, one stone carrying both tops, so there is no notch (open fault 2);
  - coping joints rebated, so each slab bears on the one below.
- **Rake cuts.** The last stone of each course under the rake is chosen long enough that the rake cut leaves a trapezoid face. No face is narrower than 50 mm or more acute than 25° (no slivers).
- **Wall ends** are heads of the biggest stones, ties and runners alternating, with a square topstone (fault 4's loose fan goes).

**SN3 Steps.** Block steps of split slate, as the record says.
- **Across:** one or two stones a step, never three, never pieced in depth. A joint falls outside the walking line's middle third, alternating sides, and no joint lies within 150 mm of the joint on the step below (no running joint).
- **Lap:** each step's front bears on the back of the one below, lapping 40 to 60 mm.
- **Ends:** both ends go 150 mm into the walls.
- **Rests** keep the plan's form: two to four large slabs, joggled, or setts in a kerb where the plan has setts.
- The 1952 reset run stays a fact: bedded in cement, joints struck.

**SN4 Form.** A stone is drawn as a mason leaves it, with few, large, planar marks.
- **The face outline:** four to seven straight edges; zero to two knocked corners, each a planar chip; no per-vertex noise anywhere.
- **Beds and arrises:** beds flat, arrises square.
- **Chamfers:** every exposed arris has a chamfer of 8 to 12 mm, at least 2 px at 5 m (the near tier's reach). The nosing's rounding is wear, from the facts.
- **A split face:** at most three planar facets, stepped at least 15 mm where laminae broke. Finer relief lives in the grain map.
- **The tread's top:** a grid only where the wear field varies, at most 120 mm apart across the walking line; flat elsewhere.
- **Hidden faces** (backs, beds, ends inside the wall) are deleted.

**SN5 Joints are filled.** Every joint has a fill no deeper than the joint is wide:
- soil and moss in dry work;
- mortar in the 1952 run and the 1961 panel.

Widths are 4 to 12 mm in the walls and 4 to 10 mm between tread stones. A fill's value stays above the darkest cast shadow on open ground. No open gap under 2 px at the nearest view (fault: black slots).

**SN6 Detail in texture, not triangles.** The surface comes from the grain map: metric UVs, a per-stone offset and turn, relief as normals, faded by footprint (`OS_Near`).
- Stone.shader gains specular filtering, Unity's `GeometricNormalFiltering` (Tokuyoshi and Kaplanyan), against the one-pixel lines and specks.
- The grain map is remade as a sculpt only if R4's restraint check fails on it. A texture array of sculpted face patches comes only if repetition is seen (What would change our minds).

**SN7 Restraint.** One value per stone face, and at most one accent where a fact puts it. The walking surface is the calmest part.
- **Lichen:** patches at least a quarter of the face's short side, on untrodden ends, nosings and copings only. One value step from the stone.
- **Polish:** one low-frequency field along the walking line.
- **Moss:** a soft line at the back of each tread and in the joints, more on the shaded side.
- **Fading:** every procedural mark is band-limited by its footprint and fades to its mean before it falls under 2 px, smallest first. Courses and silhouettes never fade.

**SN8 Budgets, enforced.**

Triangles at L0 (the near tier; the stair has one level until port step 5). The export fails above:

| Piece | At most | Assembly | At most |
| --- | --- | --- | --- |
| wall face stone (to its fill) | 40 | walls | 110,000 |
| coping, head, kneeler, knee, through | 120 | stairs | 40,000 |
| step stone, rest slab | 300 | the gully | 150,000 |
| sett | 24 | | |

Estimate: about 2,700 wall stones at about 32 triangles over about 140 m² of face, plus 150 copings, comes to about 100,000; 78 steps of about 1.6 stones at 250 to about 31,000; the rests about 8,000.

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
- **open ends:** every wall end is a head; every run of coping ends at a head, a kneeler or a knee;
- **chamfer width** under 2 px at 5 m.

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
   - a kneeler stands at every upward break and a knee at every downward one;
   - every step laps its neighbour and goes into both walls;
   - SN10's bond tests pass.
3. **In budget:** SN8's triangle gates pass at export, and its frame-time A/B passes at every view in drizzle and at the blue hour.
4. **Clean:** SN9's checks pass. On the golden frames, at native size:
   - one-pixel lines (a white top-hat, long pieces over 10 px) fall by at least 90% from the baseline and are none on nosings;
   - specks are none;
   - the joints' 5th percentile of L* sits above the darkest cast shadow on open ground.
5. **Restrained:**
   - at one-eighth size, the stone's busyness (edge density and high-frequency share of L*) at the street view is within 25% of the target frame's, in the same mask;
   - at every view it is at most 1.5 times the clay's beside it (thresholds checked on the grey-form sheet, where the joints alone set a floor);
   - the reviewer reads the eighth-size frames.
6. **The old faults gone,** each confirmed by a check or a native crop:
   - the four open faults: bent courses, the notch at the rest, pillows, the loose fan;
   - the three shared ones: mottled treads, black slots, one-pixel lines.
7. **Facts kept:** every mark that reads as history traces to a record event; two builds hash the same.
8. **Holds at every view:** a strict review on Fable, from native crops at eye-foot, eye-on, street, into12 and high in three lights, beside the target frame, says it holds, and says whether more than the stones must go (Q15).
9. **Proposed, not accepted:** the new golden frames and their sheet go to Øystein, who alone accepts a baseline.

## What would change our minds

- **Flat faces read as cheap at 1 to 2 m in grey form:** add sculpted face patches (a texture array of 8 to 16 per working) before adding a single triangle.
- **The rake's cut tops read as a row of small wedges under the coping:** stepped slab copings, set level, as dry wallers lay them (BTCV), A/B'd in grey form.
- **Courses read too coarse beside the board's walls (03, 09, 10):** smaller courses within SN8's gate, which then binds.
- **Over the frame budget:** first a street-tier shadow proxy (`ShadowsOnly`), then L1 early.
- **A blind review finding the budgeted stone worse at eye level than today's** (Q13's own reopen).

## The ladder

| Rung | What | Answer it gives | Unity |
| --- | --- | --- | --- |
| R0 | Today's gully A/B, at the five views in drizzle and the blue hour | the frame budget's base | yes, when the lock is free |
| R1 | Elevations in integer mm: every wall unrolled, its features first (heads, kneelers, knees, the 1961 panel's edges, fallen stones), courses filled by choosing; the steps' stones and joints; SN10's tests; a 2D sheet | the layout is a mason's, before any mesh | no |
| R2 | Grey form in Blender: the new parts and the laying through the stages, every piece one grey; SN1, SN8 and SN9's checks; a quick sheet at the judging cameras in neutral light | the form and the counts, cheaply | no |
| R3 | Grey form in Unity: the golden views in grey light, native crops, the frame-time A/B | form at the views, and the cost | yes |
| R4 | Materials: grain, the bake's fields made calm, the shader's marks and specular filtering; three lights; Done 4 and 5's frame checks | restraint and clean making | yes |
| R5 | The strict review on Fable, from a lean packet: native crops beside the target frame, the numbers, this design | the verdict | no |
| R6 | The proposed golden frames and sheet, to Øystein | his acceptance | no |

Each rung passes before the next starts. A rung that will not converge stops: judge the form in grey light, one change at a time.

**Box:** craft and design, about 1 Opus-day. Build, estimated before the pre-mortem at about 2.5 Opus-days: R1 0.3, R2 1.0, R3 0.3, R4 0.6, R5 and R6 0.3. It stops for a re-plan at 1.5 times.

**Also in 2b** (`reviews/lt1/port-handover.md`), since the baseline is redrawn anyway, after R2 and before R5:
- the plan in integer mm;
- world seed 1989 (retiring `legacySeed`);
- the eight `--` ids minted;
- slots for the wall heads;
- the seed keys renamed;
- `wall.py` adopting `write_export`.

The early cutoff, H1's fields and 2a's leftovers follow if the box allows. Otherwise they are listed for the step after.

## Risks seen before the pre-mortem

- **Thin, filled joints may make the walls read as one flat plane at 12 m.** Joints fade there by design, so the courses must hold by value and by the coping's lit line.
- **Spec filtering lives in the shared shading.** If it changes other materials' frames, it belongs to 1c, and the stone keeps its own call.
- **The shadow normal bias (0.5) may cause the orange rims.** That is the pipeline's, not the stone's: if R4 shows it, it goes to 1c with the evidence.
- **The grain map's split-face relief may itself be "a bit much."** R4 judges it.
- **`wall.py` is still a monolith** with its own build. The redraw writes its laying as functions the wall kind's stages can call later, without making it a kind now.
