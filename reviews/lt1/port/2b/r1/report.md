# R1 round 2: the gully's walls and steps as elevations

Port step 2b, rung R1, round 2 (`reviews/lt1/port/2b/design.md`, The ladder). The cheek walls and the steps are laid in integer millimetres by `blender/generators/masonry.py`, from `r1/facts.json` and the data (`kinds/wall.json`, `packs/stavanger-1989/walling.json`), then checked, timed and drawn by `tools/r1_elevations.py`. This report gives numbers and faults only, and judges no look. The coordinator passed R1 at round 2 on 23 October (`aae26e7`) and left two things, answered under The read of 23 October; no reviewer has passed those answers yet.

## In short

- **Counts against the budgets (SN8), two goings a level run (the variant laid):** 2,714 wall stones (round 1: 8,620, -69%; the design's estimate about 2,700). Against the budget the coordinator set on 23 October (R1's option A; SN8's first figures in brackets): walls L0 129,664 of 131,100 (110,000), walls L1 52,192 of 53,500 (45,000), steps L0 51,000 (170 stones at 300) of 51,000 (40,000), the gully L0 180,664 of 182,100 (150,000; round 1 laid 421,320).
- **Tests:** 44 checks and 1 report only (line of minimum trace, as the design asks). With two goings, 44 checks pass and 0 fail. With one going, 43 pass and 1 fails: SN2 coping slabs 450 to 1000 mm, 139 of 204. Laid twice in one run and once in a second process, the hashes are two goings `818b719a368ef651` the same three times; one going `d8999b350b8e8727` the same three times.
- **Visibility:** all 68 panel faces are seen from somewhere, so all are laid stone by stone and none is hidden work. Of the course faces, 130.82 m² are seen from within 8 m, 35.97 m² only from beyond 8 m (all bank faces, on fl-1), none from nowhere, and 12.01 m² lie under the ground. Adding the houses as occluders changes no faces.
- **Round 1's faults:** laps 18 to 0, four-stone crosses 5 to 0, joints through more than two courses 13 to 0. Panels that re-lay alone: 32 of 40 before, 34 of 34 now (one going: 34 of 34).
- **Data, not code:** every number that depends on the stone, its working or its era now lives in data. A mortared granite wall of the 1930s (`r1/granite-1930.json`) is laid by the same functions with no code edit. It passes every check.
- **Timing (Python, one process, the CPU):** the whole gully takes 1,305 ms to lay: 6.7 ms a m² of laid wall face and 0.4807 ms a wall stone. The bond tests take 0.04 ms a m² more. The C# port will differ.
- **What still fails:** with one going: SN2 coping slabs 450 to 1000 mm (139); 10 flags and 5 boundary cuts in the laying's own reports. All of it is under What fails, and why.

**The coordinator's read (22 October, 22:20).** Not passed. The next round starts from three decisions.
- **One course a rise.** The 140 mm maximum course came from `wall.py`. The town's own walls (`docs/references/stone/` 31 and 36) are thick split slabs, so the course range rises to cover a rise (up to about 190 mm), with one course on each step top as SN2 already allows. That roughly halves the stone count.
- **The back faces.** All four walls are parapets (`retains: false` in the clay's ground), so both faces are seen from somewhere. Measure which back faces the five judging views and the walkable ground can see before deciding how they are laid.
- **The budget.** SN8's 110k for the walls assumed 140 m² of face, and the walls have 212.5 m². Re-derive it from the faces that are seen, then hold to it.

**Answers.**

- **One course a rise: done.** The course range is now 120 to 260 mm, and a rise up to 190 mm is one course. The rises are 146 to 188 mm, so every rise is one course: one line on each step top and none between (0 lines between in all four walls). The courses under the last step are the rises themselves (146 to 188 mm, median 167). The free courses over it run from 174 down to 124 mm, and the foundation courses are 190 to 260 mm. The count fell from 8,620 to 2,714 wall stones, more than the read's "roughly halves", because the longer stones ride on the higher courses: a stone runs 180 to 850 mm, drawn 3/2 to 4/1 of its height, within SN10's 4.5.
- **The back faces: measured.** Both faces of every panel are seen from somewhere: the bank faces from the lanes and places around the gully. 14 whole bank faces on fl-1 (31.64 m²) are seen only from beyond 8 m: their nearest eyes are 8.0 to 17.5 m off, on Top Terrace, the way to D (1107, empty since 1986), the Landing. So no face is hidden work, and the bank faces are laid stone by stone like the stair faces. The method and the numbers are under The visibility measurement.
- **The budget: re-derived from the seen faces.** At SN8's own density (786 L0 and 321 L1 triangles a m² of course face), the 166.79 m² of seen course face give the walls 131,100 at L0 and 53,500 at L1. The walls lay 129,664 and 52,192, inside both. The coordinator took it on 23 October (design.md's table), and `kinds/wall.json`'s l0 and l1 hold it. The derivation and the option not taken are under The budget, re-derived.

## The read of 23 October

**The coordinator's read (23 October).** R1 passes at round 2 as a mason's layout (`aae26e7`): the budget follows option A (walls 131,100 and 53,500, steps 51,000 and 20,400, the gully 182,100 and 73,900), and SN2 now includes the three readings (one course a rise, as many goings as a whole coping needs, and the corner stone at twice its course). Two small things are left.
1. **7b is not met:** the granite record fails SN2 on two copings at fl-0's top ends. Fix it the way a mason with those stones would, with no special case for granite. Ask whether the cause is a universal rule the laying lacks, or a fact of the working or style held in the wrong place. The two candidates are re-dividing the run's last slabs, and the head's end form (square topstone or not), which might be the working's rather than the kind's. Put the fix where it belongs and say why in a few lines. The slate's hash may change only if the rule is universal and the slate's layout changes for the same reason; say which.
2. **A check for the walling table:** add `schemas/walling.schema.json`. Make `tools/validate_record.py` (or the check it already runs) validate the pack's `walling.json` and `r1/granite-1930.json` against it. Then make `kinds/wall.json`'s `l0` and `l1` triangles match the budget above, and remove the provisional mark.

**Answers.**

1. **7b: met.** With two goings the granite record passes every check (hash `2a4dfd6441c947a6`, the same twice); SN1, SN2, SN9 and SN10 pass. The cause was a rule of any wall that the laying lacked, not a fact held in the wrong place. With two goings a step climbs two courses, so a stretch that climbs an odd number of courses has one step of one course, and the laying always put it at the stretch's top, beside the level run above. At fl-0's top ends that left the granite an end run of about 670 mm: too long for its square topstone alone (at most about 400 mm) and too short for a topstone and a whole slab (at least 800 mm), with the risers' windows unable to close the gap. A mason sets out a stepped coping from its heads and puts the short step where the runs come out whole. So the short step now stays at the top unless the runs cannot then be laid, and otherwise goes to the nearest place down the stretch where they can (`masonry.py`, `Line.coping`). The gap between a topstone alone and a topstone and a whole slab is the topstone's least plus a whole slab less its most: 382 to 410 mm at the granite's ends and 289 to 361 mm at the slate's, wider than a riser's window of one going (297 mm) in both, so the slate could meet it too. In the granite the short step moves on fl-0/r (the riser at 8701, set 2 steps down) and fl-0/l (the riser at 8704, set 2 steps down); each top end is now a topstone and a whole slab (fl-0/r: 303 and 500 mm, fl-0/l: 300 and 500 mm). The slate's set-out leaves nothing unmet with its short steps at the top, so the rule changes no slate wall and its hashes are the same as before it (two goings `818b719a368ef651`, one going `d8999b350b8e8727`). The two candidates named in the read do not fit the cause. Re-dividing slabs cannot help: no division of a 670 mm run gives a square topstone and a whole slab, and the slabs either side of a riser lie on different beds. The end form stays the kind's: the square topstone is the head's form in the design (design.md, Wall ends, against fault 4's loose fan), a granite mason cuts a square block as readily as a slate waller picks one, and nothing in the record says the granite's heads end otherwise. With one going the granite still fails SN2's coping slabs, by the same nature as the slate's one going.
2. **The walling table's check: done.** `schemas/walling.schema.json` holds the table's shape: a working is a wall's (every course, stone, coping, topstone, head and through number, required together), a rebuilt panel's (its edge stones) or a stair's (its steps), integers only, and only a test table may name the workings it applies. `tools/validate_record.py` validates every pack's `walling.json` and the test tables merged into it (`r1/granite-1930.json`), and checks what the schema cannot say: each range's least no more than its most, each drawn length's fractions in order, each working's material one of the pack's, and a test table's workings not the pack's own. Its self-test breaks the table seven ways, and each is caught. The granite record's provenance was `test`, which the shared provenance words do not hold; it is now `authored`, and its `applies` marks it a test table. `kinds/wall.json` now holds l0 131,100 and l1 53,500, the walls' budget; l2 to l4 follow at the stair's ratios to L1 (10,700, 2,140, 214). Its `budgets.provisional` is now false (the kind schema requires the key). That flag also covers the shading figure, 600 µs, which is the stair's and unmeasured for walls until R3's A/B; the kind's description says so.

## The brief's five points

1. **One course a rise: answered.** As above. The ranges and their reasons are in the walling table's notes (`packs/stavanger-1989/walling.json`). The town's own walls (`docs/references/stone/` 31 and 36) are thick split slabs in level beds with the biggest stones low, so a course covers a rise. The free courses diminish upwards by up to 10 mm a course, from no more than the last rise down to 120. The foundation courses are larger than any rise, and each is at least the course over it (fixed this round, see Assumed). SN2's "a line on each step top" checks 160 step tops and "one course a rise" 156 rises, with no failure. SN10's "the largest courses low" checks 44 courses, with no failure.
2. **The back faces: answered.** I measured them from the six judging views and from standing eyes 1.6 m over all the walkable ground, by panel and face, with the terrain and the walls as occluders. All 68 faces are seen; 28 of them appear in at least one judging view. 35.97 m² of course face is seen only from beyond 8 m. No face is veiled, because none is hidden.
3. **The budget: answered; option A taken on 23 October.** Walls: L0 131,100 and L1 53,500 (option A), or L0 106,200 if the faces seen only from beyond 8 m are built at L1 alone (option B). Steps: L0 51,000 and L1 20,400, the table's 300 and 120 a stone times the 170 stones the facts make. The gully: L0 182,100 and L1 73,900.
4. **Stepped tops by SN2: answered.** There are no kneelers, knees or raked stones: SN9's "no rake" checks 2,714 stones, none sloped. Every coping lies on whole courses, and below the last step every coping steps from one step top's line to another's. Over each rest the coping runs level (14 rest runs, each rest on both walls, no riser on any) and drops square at the next flight. Every coping run ends at a head's topstone or at a square step (261 ends checked, none open). Both variants are laid. I pick **two goings** a level run: a going is 296 to 297 mm here (median 297), so a run over one going leaves a slab of about 300 mm, under a whole slab's 450 mm. With one going, 139 of 204 slabs are short. With two goings, all 144 slabs are 450 to 994 mm (median 592). The coping then steps 9 times by 1 course, 72 times by 2 courses, 124 to 356 mm (median 330); with one going it steps 155 times by 1 course, 124 to 188 mm. The design leaves the final choice to R2b's grey form, by how the stepped top reads; this is R1's evidence for it. The one-going variant's stair faces are on the sheet for comparison.
5. **Round 1's other faults: answered.** Laps: 18 failures to 0. Crosses: 5 to 0. Joints through more than two courses: 13 to 0 (round 1's 13 included 8 at the topstones; now 0). Panels changing stones outside themselves: 8 of 40 to 0 of 34. The steps' 9 mm play and fl-1's rests are by the facts, and I propose no rule change for them, since nothing here is evidence against the rules. Each is under What fails, and why.

## Tests

Each check counts what it looked at and lists what failed. The one-going variant is checked by the same tests. New this round, from the self-check: SN9's overlap and contact in the elevation (each face's courses tiled with no overlap and no gap, every stone in its course's length or, if two-faced, under the other face's footing, and nothing in a step's end), and the heads' alternation counted up each face.

| Rule | Check | Two goings: checked | failed | One going: checked | failed |
| --- | --- | --- | --- | --- | --- |
| SN1 | convex | 2714 | 0 | 2769 | 0 |
| SN1 | integer outlines | 2714 | 0 | 2769 | 0 |
| SN10 | laps | 2638 | 0 | 2754 | 0 |
| SN10 | line of minimum trace | reported | - | reported | - |
| SN10 | no four-stone cross | 2638 | 0 | 2754 | 0 |
| SN10 | no joint through more than two courses | 2638 | 0 | 2754 | 0 |
| SN10 | no stone over 4.5 x its height | 2562 | 0 | 2557 | 0 |
| SN10 | the largest courses low | 44 | 0 | 44 | 0 |
| SN2 | a line on each step top | 160 | 0 | 160 | 0 |
| SN2 | a step falls only on a step top's line | 70 | 0 | 136 | 0 |
| SN2 | a stepped section's corner stone at least 2 x its height | 312 | 0 | 312 | 0 |
| SN2 | bank footing in whole courses | 156 | 0 | 156 | 0 |
| SN2 | coping slabs 450 to 1000 mm | 144 | 0 | 204 | 139 |
| SN2 | copings on whole courses | 83 | 0 | 157 | 0 |
| SN2 | course heights 120 to 260 | 200 | 0 | 200 | 0 |
| SN2 | every course ends at a feature | 710 | 0 | 710 | 0 |
| SN2 | heads: ties and runners alternate | 16 | 0 | 16 | 0 |
| SN2 | level beds on course lines | 2714 | 0 | 2769 | 0 |
| SN2 | no angle under 25 degrees | 2714 | 0 | 2769 | 0 |
| SN2 | no face under 50 mm | 2714 | 0 | 2769 | 0 |
| SN2 | no stone under 50 mm high | 2562 | 0 | 2557 | 0 |
| SN2 | one course a rise | 156 | 0 | 156 | 0 |
| SN2 | over a rest the coping runs level | 14 | 0 | 14 | 0 |
| SN2 | risers only where the pitch rises | 83 | 0 | 157 | 0 |
| SN2 | square topstones | 8 | 0 | 8 | 0 |
| SN3 | ends 150 mm into the walls | 81 | 0 | 81 | 0 |
| SN3 | joint outside the middle third | 71 | 0 | 71 | 0 |
| SN3 | joints alternate | 69 | 0 | 69 | 0 |
| SN3 | laps 40 to 60 mm | 77 | 0 | 77 | 0 |
| SN3 | never pieced in depth | 71 | 0 | 71 | 0 |
| SN3 | no joint within 150 mm of the one below | 83 | 0 | 83 | 0 |
| SN3 | one or two stones a step | 71 | 0 | 71 | 0 |
| SN3 | rests: two to four slabs | 8 | 0 | 8 | 0 |
| SN3 | within the finish's sizes | 170 | 0 | 170 | 0 |
| SN4 | 4 to 7 edges | 2714 | 0 | 2769 | 0 |
| SN5 | tread joints 4 to 10 mm | 85 | 0 | 85 | 0 |
| SN8 | seen faces are laid | 68 | 0 | 68 | 0 |
| SN9 | no rake | 2714 | 0 | 2769 | 0 |
| SN9 | nothing in a step's end | 1309 | 0 | 1361 | 0 |
| SN9 | open ends | 261 | 0 | 483 | 0 |
| SN9 | the faces tiled: every stone in its place | 3001 | 0 | 3117 | 0 |
| SN9 | the faces tiled: no gap | 355 | 0 | 355 | 0 |
| SN9 | the faces tiled: no overlap | 362 | 0 | 362 | 0 |
| ids | ids are unique | 1 | 0 | 1 | 0 |
| ids | ids follow the grammar | 2884 | 0 | 2939 | 0 |

Failures and notes, two goings unless marked:

**SN10, laps.** 

- wl-gully/fl-0/r bank at 1844: the rebuilt panel's edge, a straight joint by the facts (exempt), in 7 courses
- wl-gully/fl-0/r bank at 6226: the rebuilt panel's edge, a straight joint by the facts (exempt), in 6 courses
- wl-gully/fl-0/r stair at 1844: the rebuilt panel's edge, a straight joint by the facts (exempt), in 4 courses
- wl-gully/fl-0/r stair at 6226: the rebuilt panel's edge, a straight joint by the facts (exempt), in 3 courses

**SN10, line of minimum trace.** reported per laid panel face

- 68 laid panel faces with a stack of three or more jointed courses: the least trace is 1.12 times the height, the median 1.93, the most 2.75 (1.00 is a straight joint). The five lowest:
  - wl-gully/fl-0/r/pn-3 stair: 1.12 times the height over courses 19 to 23 (835 mm; 1.00 is a straight joint)
  - wl-gully/fl-1/r/pn-3 stair: 1.35 times the height over courses 17 to 22 (993 mm; 1.00 is a straight joint)
  - wl-gully/fl-1/l/pn-3 stair: 1.38 times the height over courses 17 to 22 (993 mm; 1.00 is a straight joint)
  - wl-gully/fl-0/r/pn-3 bank: 1.39 times the height over courses 16 to 23 (1327 mm; 1.00 is a straight joint)
  - wl-gully/fl-1/r/pn-11 stair: 1.47 times the height over courses 44 to 49 (1008 mm; 1.00 is a straight joint)

**SN10, no joint through more than two courses.** no vertical joint through more than two courses

- wl-gully/fl-0/r stair: the longest run of joints within a lap of each other spans 2 courses (a two-course head's side counts as two); the rebuilt panel's edge, a straight joint by the facts, runs 5
- wl-gully/fl-0/r bank: the longest run of joints within a lap of each other spans 2 courses (a two-course head's side counts as two); the rebuilt panel's edge, a straight joint by the facts, runs 8
- wl-gully/fl-0/l stair: the longest run of joints within a lap of each other spans 2 courses (a two-course head's side counts as two)
- wl-gully/fl-0/l bank: the longest run of joints within a lap of each other spans 2 courses (a two-course head's side counts as two)
- wl-gully/fl-1/r stair: the longest run of joints within a lap of each other spans 2 courses (a two-course head's side counts as two)
- wl-gully/fl-1/r bank: the longest run of joints within a lap of each other spans 2 courses (a two-course head's side counts as two)
- wl-gully/fl-1/l stair: the longest run of joints within a lap of each other spans 2 courses (a two-course head's side counts as two)
- wl-gully/fl-1/l bank: the longest run of joints within a lap of each other spans 2 courses (a two-course head's side counts as two)

**SN2, bank footing in whole courses.** on the bank side the footing steps with the ground, each step a whole course

- wl-gully/fl-0/r: 29 footing steps, the shortest inner tread 300 mm
- wl-gully/fl-0/l: 29 footing steps, the shortest inner tread 300 mm
- wl-gully/fl-1/r: 50 footing steps, the shortest inner tread 300 mm
- wl-gully/fl-1/l: 48 footing steps, the shortest inner tread 300 mm

**SN2, coping slabs 450 to 1000 mm.** a coping slab 450 to 1000 mm long (wall.py)

- one going: 139 failures, e.g. wl-gully/fl-0/r/pn-0/cp-0 267 mm; wl-gully/fl-0/r/pn-0/cp-1 309 mm; wl-gully/fl-0/r/pn-0/cp-2 298 mm; wl-gully/fl-0/r/pn-0/cp-3 287 mm

**SN2, every course ends at a feature.** each course ends at the wall's end, a step's end or the ground's step, a topstone, or a stepped section's end (the riser)

- wl-gully/fl-0/r: course ends by kind {'end': 18, 'feature': 4, 'ground': 28, 'riser': 32, 'riser-open': 28, 'step': 30}
- wl-gully/fl-0/l: course ends by kind {'end': 18, 'feature': 4, 'ground': 28, 'riser': 32, 'riser-open': 28, 'step': 30}
- wl-gully/fl-1/r: course ends by kind {'end': 17, 'feature': 4, 'ground': 49, 'riser': 50, 'riser-open': 46, 'step': 48}
- wl-gully/fl-1/l: course ends by kind {'end': 19, 'feature': 4, 'ground': 47, 'riser': 52, 'riser-open': 46, 'step': 48}

**SN3, joint outside the middle third.** the joint falls outside the walking line's middle third (|x| >= 536 mm)

- st-gully/fl-0: a step's joint can start only in [-548, -540] or [536, 544] mm (9 mm of play a side): two stones of at most 2300 mm across 3512 mm, the joint outside the middle third (536 mm either side of the walking line)
- st-gully/fl-0/tr-14 row [4153, 5799]: a rest's joint at 386 lies inside the middle third (two slabs of at most 2300 across 3512 mm must meet within 544 mm of the centre; SN3 puts the rule on steps)
- st-gully/fl-1: a step's joint can start only in [-548, -540] or [536, 544] mm (9 mm of play a side): two stones of at most 2300 mm across 3512 mm, the joint outside the middle third (536 mm either side of the walking line)
- st-gully/fl-1/turn row [0, 1654]: a rest's joint at -65 lies inside the middle third (two slabs of at most 2300 across 3512 mm must meet within 544 mm of the centre; SN3 puts the rule on steps)
- st-gully/fl-1/tr-7 row [3677, 4948]: a rest's joint at 241 lies inside the middle third (two slabs of at most 2300 across 3512 mm must meet within 544 mm of the centre; SN3 puts the rule on steps)
- st-gully/fl-1/tr-7 row [4948, 6747]: a rest's joint at 427 lies inside the middle third (two slabs of at most 2300 across 3512 mm must meet within 544 mm of the centre; SN3 puts the rule on steps)
- st-gully/fl-1/tr-14 row [8476, 10049]: a rest's joint at 155 lies inside the middle third (two slabs of at most 2300 across 3512 mm must meet within 544 mm of the centre; SN3 puts the rule on steps)
- st-gully/fl-1/tr-14 row [10049, 11545]: a rest's joint at -208 lies inside the middle third (two slabs of at most 2300 across 3512 mm must meet within 544 mm of the centre; SN3 puts the rule on steps)
- st-gully/fl-1/tr-20 row [12977, 14230]: a rest's joint at 317 lies inside the middle third (two slabs of at most 2300 across 3512 mm must meet within 544 mm of the centre; SN3 puts the rule on steps)
- st-gully/fl-1/tr-20 row [14230, 15937]: a rest's joint at 167 lies inside the middle third (two slabs of at most 2300 across 3512 mm must meet within 544 mm of the centre; SN3 puts the rule on steps)
- st-gully/fl-1/tr-26 row [17361, 19296]: a rest's joint at -123 lies inside the middle third (two slabs of at most 2300 across 3512 mm must meet within 544 mm of the centre; SN3 puts the rule on steps)
- st-gully/fl-1/tr-26 row [19296, 20661]: a rest's joint at 334 lies inside the middle third (two slabs of at most 2300 across 3512 mm must meet within 544 mm of the centre; SN3 puts the rule on steps)
- st-gully/fl-1/tr-34 row [22695, 24488]: a rest's joint at 365 lies inside the middle third (two slabs of at most 2300 across 3512 mm must meet within 544 mm of the centre; SN3 puts the rule on steps)
- st-gully/fl-1/tr-34 row [24488, 26254]: a rest's joint at 185 lies inside the middle third (two slabs of at most 2300 across 3512 mm must meet within 544 mm of the centre; SN3 puts the rule on steps)
- st-gully/fl-1/tr-41 row [27978, 29847]: a rest's joint at 22 lies inside the middle third (two slabs of at most 2300 across 3512 mm must meet within 544 mm of the centre; SN3 puts the rule on steps)
- st-gully/fl-1/tr-41 row [29847, 31677]: a rest's joint at -146 lies inside the middle third (two slabs of at most 2300 across 3512 mm must meet within 544 mm of the centre; SN3 puts the rule on steps)

**SN3, rests: two to four slabs.** a rest keeps the plan's form: two to four large slabs

- st-gully/fl-1/tr-7: 3070 mm deep, over the longest slab (2300): four slabs in two rows where the plan names two
- st-gully/fl-1/tr-14: 3069 mm deep, over the longest slab (2300): four slabs in two rows where the plan names two
- st-gully/fl-1/tr-20: 2960 mm deep, over the longest slab (2300): four slabs in two rows where the plan names two
- st-gully/fl-1/tr-26: 3300 mm deep, over the longest slab (2300): four slabs in two rows where the plan names two
- st-gully/fl-1/tr-34: 3559 mm deep, over the longest slab (2300): four slabs in two rows where the plan names two
- st-gully/fl-1/tr-41: 3699 mm deep, over the longest slab (2300): four slabs in two rows where the plan names two

## Counts (SN8)

| Wall line | Stones | By kind | Laid face m² | L0 | L1 |
| --- | --- | --- | --- | --- | --- |
| wl-gully/fl-0/r | 387 | coping 18, face (bank) 220, face (stair) 132, head runner 4, head tie 3, through 8, topstone 2 | 27.09 | 18,360 | 7,392 |
| wl-gully/fl-0/l | 364 | coping 18, face (bank) 200, face (stair) 128, head runner 5, head tie 2, through 9, topstone 2 | 26.8 | 17,488 | 7,024 |
| wl-gully/fl-1/r | 1052 | coping 54, face (bank) 563, face (stair) 397, head runner 5, head tie 2, through 29, topstone 2 | 75.91 | 49,648 | 19,984 |
| wl-gully/fl-1/l | 911 | coping 54, face (bank) 410, face (stair) 407, head runner 4, head tie 4, through 30, topstone 2 | 64.84 | 44,168 | 17,792 |
| st-gully/fl-0 (steps) | 60 | step 58, rest 2 | | 18,000 | 7,200 |
| st-gully/fl-1 (steps) | 110 | landing 2, step 84, rest 24 | | 33,000 | 13,200 |

| | Round 1 | Two goings | One going | Design (SN8) |
| --- | --- | --- | --- | --- |
| wall stones | 8,620 | 2,714 | 2,769 | about 2,700 |
| face stones | 8,301 | 2,457 | 2,451 |  |
| copings | 106 | 144 | 204 | about 150 |
| kneelers and knees | 40 | 0 | 0 |  |
| throughs | 71 | 76 | 77 |  |
| head stones | 96 | 29 | 29 |  |
| topstones | 6 | 8 | 8 |  |
| laid face m² (courses, copings and topstones) | 212.50 | 194.63 | 194.80 | about 140 |
| step stones and slabs | 170 | 170 | 170 | about 78 steps of 1.6 |
| walls L0 | 370,320 | 129,664 | 136,744 | 110,000 |
| walls L1 |  | 52,192 | 55,024 | 45,000 |
| stairs L0 | 51,000 | 51,000 | 51,000 | 40,000 |
| the gully L0 | 421,320 | 180,664 | 187,744 | 150,000 |
| the gully L1 |  | 72,592 | 75,424 | 65,000 |

The triangles are SN8's table: a face stone 40 at L0 and 16 at L1; a coping, head, through or topstone 120 and 48; a step stone or slab 300 and 120; a laid panel face's fill 8. The laid face is 85.32 m² on the stair side and 109.3 m² on the bank side, coping faces and the ground's buried strip included. That is 14.7 face stones a m² of seen course face, and 777 L0 triangles a m², against SN8's 786.

**How long the laying takes.** This is CPython, in one process on one thread, on Apple M4 (Mac16,10). Each time is the median of 5 runs, measured with `time.perf_counter` around each part. The C# port will differ: it will have other data structures, no interpreter, and possibly other searches, so these numbers size the work but are not the C# cost.

| | ms | ms a m² of laid face | ms a stone |
| --- | --- | --- | --- |
| the whole gully, walls and steps (two goings) | 1,305.2 | 6.71 | 0.4526 |
| the walls alone | 1,304.7 | 6.7 | 0.4807 |
| the largest panel's fill (wl-gully/fl-0/l/pn-2, 11.53 m², 149 stones) | 1.25 | 0.11 | 0.0084 |
| that panel's line re-laid for an event in it, every feature included | 51.1 | | |
| the bond tests (SN10, in this tool, not the laying) | 7.8 | 0.04 | 0.0029 |
| the one-going variant, the whole gully (3 runs) | 3,851.4 | 19.77 | 1.3104 |

| Part of the laying | ms | share |
| --- | --- | --- |
| fill: teeth | 1062.91 | 82% |
| features: heads | 124.44 | 10% |
| features: falls | 54.3 | 4% |
| fill: courses | 26.28 | 2% |
| features: footings | 12.06 | 1% |
| features: throughs | 10.07 | 1% |
| features: coping | 5.77 | 0% |
| fill: falls on, ids, output | 4.18 | 0% |
| features: regions | 3.02 | 0% |
| steps | 0.48 | 0% |
| features: course lines | 0.13 | 0% |

Features take 209.8 ms (16%), the fill 1093.4 ms (84%) and the steps 0.48 ms. The fill keeps the bond itself: each stone's length is chosen clear of the joints below and above, so the laying has no separate bond pass, and the bond tests above are only this tool's check. The other tests take 57.8 ms. For a city: 89.6 m of wall line, with 2.17 m² of laid face a metre of line (both faces, copings and the buried strip included), take 14.6 ms a metre of line to lay, so about 15 s a kilometre of such wall, in this Python. Nothing was changed for speed.

## The visibility measurement

`tools/r1_elevations.py visibility` measures which panel faces are seen. Its method, as written into `facts.json`:

- **faces:** a sample every 220 mm along each course at its mid-height, on the face battered 1 in 6 (wall.py), 20 mm off it; a sample is buried where the ground 0.1 m outside the face stands over it.
- **eyes:** the six judging views (LT1Stone.cs, in frame at 2560 x 1440) and standing eyes 1.6 m over the walkable ground: every lane, stair and quay of heart_layout.LANES every 1.75 m along and about 1.5 m across (0.3 m in from the edges), the Landing, the small places, the market square and the yards on a 1.5 m grid, none inside a house.
- **ground:** the clay's carved ground on its 1.5 m grid (heart_layout.carve over centre_land.heights, as wall.py's ground_near), bilinear; inside each flight's clear width the steps' treads.
- **rays:** from the sample to the eye, if the eye is in front of the face; blocked by another wall line (its top as a slab 0.15 to 0.57 m outside the stair's clear half-width, under its coping's top) or by the ground (marched every 0.5 m, 20 mm under it); houses do not block (sensitivity.withHouses adds them).
- **classes:** near: seen from an eye within 8 m (L0's range); farOnly: seen only from farther, up to 80 m; unseen: from nowhere within 80 m; buried: under the ground.
- **measuredOn:** the two-going layout's courses and copings, before any fill.
- **counts:** 5,244 samples; 6 judging views, 4,585 eyes on lanes, stairs and quays, 164 on the places, 18 in the yards (11 dropped inside houses). 5,915 rays from the views, 120,000 from the walkable ground (each sample stops at its first clear ray, nearest eyes first).
- **time:** 5.1 s to measure, after 65.8 s to import the clay's layout.

| Face | Seen within 8 m | Seen only beyond 8 m | Seen from nowhere | Buried | Faces laid |
| --- | --- | --- | --- | --- | --- |
| stair | 77.39 | 0.0 | 0.0 | 0.02 | 34 of 34 |
| bank | 53.43 | 35.97 | 0.0 | 11.99 | 34 of 34 |
| both | 130.82 | 35.97 | 0.0 | 12.01 | 68 of 68 |

The area is in m² of course face (copings and topstones are not sampled: they are 15.83 m² more, and seen from every side). **35.97 m² is seen only from beyond 8 m.** 31.64 m² of it is in 14 whole faces, every one a bank face on fl-1: fl-1/l/pn-2 bank, fl-1/l/pn-3 bank, fl-1/l/pn-4 bank, fl-1/l/pn-5 bank, fl-1/l/pn-6 bank, fl-1/l/pn-7 bank, fl-1/l/pn-8 bank, fl-1/r/pn-3 bank, fl-1/r/pn-4 bank, fl-1/r/pn-5 bank, fl-1/r/pn-6 bank, fl-1/r/pn-7 bank, fl-1/r/pn-8 bank, fl-1/r/pn-9 bank. The rest is in fl-1/l/pn-1 bank, fl-1/l/pn-9 bank, fl-1/r/pn-10 bank, fl-1/r/pn-2 bank, which are also seen from near.

The far-only area is not seen from far off. Its nearest clear eye on the walkable ground is 8.0 to 17.5 m away (median 12.4), standing on Top Terrace, 20.19 m²; the way to D (1107, empty since 1986), 10.49 m²; the Landing, 5.28 m². So those faces sit in L1's range, never in L0's.

**Sensitivity.** Without the yards (they may not be walkable in play), no faces change. With eyes out to 120 m, no faces change. With the clay's 99 houses as occluders too (boxes over their footprints to their eaves, roofs left out), no faces change; on the bank side the area seen within 8 m falls from 53.43 to 52.03 m², the far-only area rises to 37.37 m², and none is seen from nowhere. The result does not rest on leaving the houses out.

The sheet `visibility.png` shows each sample by its class: near, far only, unseen, or buried.

## The budget, re-derived (option A taken on 23 October)

SN8 sets the walls at 110,000 L0 and 45,000 L1 for about 140 m² of face. Its estimate counts 140 m² of course face for the face stones and adds the copings, so its density is 786 L0 and 321 L1 triangles a m² of course face, copings included.

- **A (taken): every seen face at L0.** 166.79 m² of seen course face (130.82 within 8 m plus 35.97 only beyond) gives L0 786 × 166.79 = 131,100 and L1 321 × 166.79 = 53,500. The buried 12.01 m² is left out: it is laid because its faces are seen, but nobody sees it. The walls lay 129,664 L0 (1,436 under) and 52,192 L1 (1,308 under).
- **B: the faces seen only from beyond 8 m built at L1 alone.** L0 786 × (166.79 − 31.64) = 106,200; L1 as A. Those faces hold 497 face stones, which would have no L0, so the walls' L0 count becomes 109,672. B saves only memory and export time: L0 is drawn within 8 m anyway, so frame time does not change. It also ties the mesh to today's eyes, so B belongs to step 5's chunks, if anywhere.
- **Steps.** SN8's 40,000 assumed 78 steps of about 1.6 stones at 250 triangles, and 8,000 for the rests. The facts give 71 steps of two stones each and 8 rests and landings of 28 slabs, so 170 stones. One stone cannot span a step: the stair is 3512 mm between the walls' faces with the ends in them, and the longest slab is 2300. Proposed: L0 51,000 and L1 20,400, the table's 300 and 120 a stone. The other way is to hold 40,000 at 235 triangles a stone, which R2b's step part would have to meet.
- **The gully,** A plus the steps: L0 182,100 and L1 73,900, against SN8's 150,000 and 65,000. It lays 180,664 and 72,592.

The coordinator took A and the steps' 51,000 on 23 October: design.md's table now reads walls 131,100 and 53,500, steps 51,000 and 20,400, the gully 182,100 and 73,900, with frame time as the real cap. `kinds/wall.json`'s l0 and l1 hold the walls' (131,100 and 53,500).

## The laying's own reports

Two goings. 10 flags, 5 boundary cuts, 0 free lengths laid with less than the full rule, 8 fall points not placed, 6 through stones not placed.

**wl-gully/fl-0/r.**

- fall at s 7344, z 7329: in course 28 where a feature or head stands: not placed
- through stone not placed in wl-gully/fl-0/r/pn-0 at 166: no course with room on both faces
- cut: wl-gully/fl-0/r stair course 19: the 1961 edge at 6226 is the course's end against the step at 6348, 122 mm off it (no stone fits between them); the stone at that end is the panel's that holds its middle
- cut: wl-gully/fl-0/r bank course 5: the 1961 edge at 1844 is the course's end against the ground at 2000, 156 mm off it (no stone fits between them); the stone at that end is the panel's that holds its middle
- flag: wl-gully/fl-0/r stair course 17: the tooth at 5664 is 117 mm off it, over 90

**wl-gully/fl-0/l.**

- fall at s 7649, z 6886: held (the facts: bedded in mortar, in the rebuilt panel or a patched hole)
- fall at s 2366, z 4877: fell: course 13, 2147 to 2431
- through stone not placed in wl-gully/fl-0/l/pn-2 at 10096: no course with room on both faces
- cut: wl-gully/fl-0/l bank course 16: the boundary at 5769 is the course's end against the ground at 5800, 31 mm off it (no stone fits between them); the stone at that end is the panel's that holds its middle
- flag: wl-gully/fl-0/l bank course 11: the tooth at 4041 is 121 mm off it, over 90

**wl-gully/fl-1/r.**

- fall at s 596, z 8643: fell: course 5, 402 to 809
- fall at s 5953, z 10005: fell: course 14, 5740 to 6433
- fall at s 2867, z 9237: fell: course 9, 2577 to 3105
- through stone not placed in wl-gully/fl-1/r/pn-0 at 240: no course with room on both faces
- through stone not placed in wl-gully/fl-1/r/pn-0 at 1116: no course with room on both faces
- through stone not placed in wl-gully/fl-1/r/pn-8 at 22085: no course with room on both faces
- cut: wl-gully/fl-1/r bank course 44: the boundary at 31656 is the course's end against the ground at 31700, 44 mm off it (no stone fits between them); the stone at that end is the panel's that holds its middle
- flag: wl-gully/fl-1/r stair course 43: the tooth at 27872 is 124 mm off it, over 90
- flag: wl-gully/fl-1/r bank course 10: the tooth at 6742 is 122 mm off it, over 90

**wl-gully/fl-1/l.**

- fall at s 32785, z 16510: fell: course 53, 32573 to 32889
- fall at s 27662, z 15598: fell: course 47, 27418 to 27952
- through stone not placed in wl-gully/fl-1/l/pn-8 at 22082: no course with room on both faces
- cut: wl-gully/fl-1/l bank course 40: the boundary at 27872 is the course's end against the ground at 27900, 28 mm off it (no stone fits between them); the stone at that end is the panel's that holds its middle
- flag: wl-gully/fl-1/l/hd-0/st-1: 193 mm, outside its range (220, 320), to leave whole stones beside it
- flag: wl-gully/fl-1/l stair course 43: the tooth at 27872 is 124 mm off it, over 90
- flag: wl-gully/fl-1/l bank course 6: the tooth at 3413 is 44 mm off it, under 50, to keep its laps
- flag: wl-gully/fl-1/l bank course 25: the tooth at 15913 is 119 mm off it, over 90
- flag: wl-gully/fl-1/l bank course 38: the tooth at 26232 is 116 mm off it, over 90
- flag: wl-gully/fl-1/l: the fallen stone at 27662 lies within 308 mm of a panel's boundary

**The rules that place the features, and why** (each found by a failure in this round's runs, fixed at its cause):

- **Risers move within their window** (half a going either side of where the ideal bed puts them), by three rules in order. 10 of 83 risers moved:
  - wl-gully/fl-0/r riser at 1844 (ideal 1798): onto the straight joint at 1844
  - wl-gully/fl-0/r riser at 4041 (ideal 4036): +5 mm, so the runs either side are whole slabs
  - wl-gully/fl-0/r riser at 5664 (ideal 5769): -105 mm, so its corner stones and the edge's fit before the straight joint at 6226
  - wl-gully/fl-0/r riser at 9288 (ideal 9330): -42 mm, so the runs either side are whole slabs
  - wl-gully/fl-0/l riser at 4041 (ideal 4036): +5 mm, so the runs either side are whole slabs
  - wl-gully/fl-0/l riser at 9295 (ideal 9334): -39 mm, so the runs either side are whole slabs
  - wl-gully/fl-1/r riser at 8349 (ideal 8341): +8 mm, so the runs either side are whole slabs
  - wl-gully/fl-1/l riser at 8349 (ideal 8341): +8 mm, so the runs either side are whole slabs
  - wl-gully/fl-1/l riser at 32123 (ideal 32196): -73 mm, so the runs either side are whole slabs
  - wl-gully/fl-1/l riser at 32573 (ideal 32683): -110 mm, so the runs either side are whole slabs
  1. *A straight joint:* a riser within a lap of a rebuilt panel's edge snaps onto it. If it is just above the edge, it moves until its stepped section's corner stone (at least twice the course's height) and the edge's stone both fit before the joint. Before this rule, fl-0/r's riser at 5769 left 457 mm to the 6226 edge, and the corner and the edge stone could not both be laid.
  2. *Whole slabs:* between two risers the run takes whole slabs (450 to 1000 mm), pushing the next riser along within its window where it must.
  3. *The end runs:* a wall's end run is either its topstone alone or a topstone and a whole slab.
- **The short step goes where the runs can be laid** (the read of 23 October). Where a stretch climbs a number of courses that is not a whole number of steps, its one short step stays at the stretch's top unless the rules above then leave something unmet; otherwise it goes to the nearest place down the stretch that leaves less unmet. It moves no slate step (0 moved) and 2 of the granite record's.
- **Panels are bounded at the rests' coping run ends** and at the rebuilt panel's edges. A wall's ends are its heads, not panel boundaries. This gives 34 panels where round 1 had 40.
- **Teeth look one course ahead:** a boundary's tooth in a course is chosen so the course above still has a lapped tooth of at least 50 mm. Where none fits in 50 to 90, it goes up to 128 (flagged), and below 50 only to keep its laps (flagged).
- **The end stones' rules hold for every stone laid first** (heads, teeth, falls and throughs): a stepped section's corner stone at least 2 times its height, and the rebuilt panel's edge stones long and short in alternate courses.
- **The heads keep clear of the joints fixed above and below them**: the risers' corner joints, the stones laid first, and the coping joints over the top course.
- **Each face's head stands on that face's own footing.** A tie runs through both faces only in courses where both faces stand at the wall's end; below the higher footing the lower face goes on alone, a header or a runner by the head's order, in its own courses. Before this rule the head started both faces at the lower footing, so at the top ends of fl-0/l and fl-1/r a stair-face stone stood under the top step's level, in the last steps' ends (st-gully/fl-0/tr-28 and tr-29, st-gully/fl-1/tr-47), and the granite record's fl-0/r tie did the same. SN9's new tiling checks found it in the self-check; no other check had looked.

## Panels re-laid one at a time

Each panel is re-laid with an event's seed on its own id, and every stone that changes is counted.

- **Two goings:** 34 of 34 panels change only their own stones (from 4 to 142 of them).
- **One going:** 34 of 34 panels change only their own stones (from 7 to 151 of them).
- Round 1: 32 of 40. The leaks were at boundaries where a course took no tooth, so one stone crossed the boundary. Now such a course ends against the ground or a step, and the report names it as a cut (above).

## What lives in data, and what stays in code

Changing style, era or world must be a data edit (the coordinator, for Øystein; design.md 7b). `masonry.py` reads every number that depends on the stone, its working, its era or the style into a `Rules`, from two files:

- **The pack's walling table, `packs/stavanger-1989/walling.json`**, by the working a wall's facts name (`dry-split-1874`, its 1961 rebuild `cement-relaid-1961`). It holds the stone's and the builders' numbers: the course heights (`courseMm`, `riseOneMm`, `foundationMm`); the stones (`stoneMm`, `drawnPerHeight`, `shortMm`); the copings (`copeThickMm`, `copeNominalMm`, `copeLengthMm`, `copeLeastMm`); the topstones, head ties and runners (`topstoneMm`, `headTieMm`, `headRunnerMm`); the through stones (`throughMm`, `throughFirstMm`, `throughEveryMm`); a rebuilt panel's edge stones (`edgeStonesMm`); and the steps' laps and joints (`steps`). Each value has a note with its reason and source. Round 1 had all of these as module constants.
- **The wall kind, `kinds/wall.json`**, beside `kinds/stair.json`, in `schemas/kind.schema.json`'s shape. Its plan params hold the wall's structure: the parapet's height, one or two goings a level run, a head's courses, the topstone's squareness, a stepped section's corner stone, the free courses' step, the bank footing's tread, the panels' teeth, the throughs' clearance and shift, and where the steps' ends sit in the walls.
- **In code, the rules of any wall:** level beds and no rake; SN2's sliver (50 mm) and acute (25°) limits; SN10's bond (no stone over 4.5 times its height, a lap of 0.4 of the course and at least 40 mm, the four-stone cross, joints through more than two courses); a stone falls when nine tenths of its bed is gone. Two more numbers stay in code because they are only the search's resolution and reach (5 mm steps for a through stone, 300 mm of free courses over the top), not facts about any wall. `Rules` also checks the data against the code's rules, so a bad edit raises an error and is never laid quietly.
- **Gone with the stepped tops:** round 1's kneelers, knees, raked copings and their numbers.
- **What the schemas cannot hold.** `schemas/material.schema.json` refuses a walling section (`additionalProperties: false`), so I did not put one into `materials/slate.json`. The walling table is a pack table in `stairs.json`'s format instead, keyed by working, with each working naming its material. Since the read of 23 October `schemas/walling.schema.json` validates it, and the granite test table, through `tools/validate_record.py` (see The read of 23 October); `stairs.json` still has no schema. The validator passes with `kinds/wall.json` in the registry.
- **Joint widths** between wall stones are not modelled at R1: the stones meet at their outlines. When R2's geometry needs them, they belong in the working (a dry slate's few mm against a mortared granite's 10 to 15 mm). The steps' tread joints (4 to 10 mm, SN5) are in the walling table already.

### The granite record (design.md 7b)

`r1/granite-1930.json` is a test record, not researched, in the walling table's shape. It holds two workings no gully wall has: `mortared-granite-1930` (squared granite in level mortared courses, 140 to 340 mm high, stones 300 to 1200 mm, slab copes 500 to 1200 mm) and `cement-relaid-granite-1961`. The tool merges them into a copy of the pack's table, points the facts' walls and their rebuilt panel at them, and lays and tests the same walls with the same functions. No code changes.

- **Laid:** hash `2a4dfd6441c947a6`, again `2a4dfd6441c947a6` (the same). 2,265 wall stones, 130 copings, 48 throughs; walls L0 108,264 and L1 43,632.
- **Tests:** 44 checks, 44 pass, 0 fail. SN1, SN2, SN9 and SN10 pass.
- **The laying's reports:** 17 flags, 43 cuts, 2 free lengths laid with less of the rule: stones under 300 mm, bonded.
- **The set-out:** the short step moved down its stretch on fl-0/r, riser at 8701 (ideal 8707): -6 mm, so the runs either side are whole slabs; the stretch's short step, set 2 steps down from its top so its runs can be laid whole; fl-0/l, riser at 8704 (ideal 8710): -6 mm, so the runs either side are whole slabs; the stretch's short step, set 2 steps down from its top so its runs can be laid whole. See The read of 23 October.
- **One going:** hash `90c78326332e95e1` (stable); SN2 a stepped section's corner stone at least 2 x its height fails 2; SN2 coping slabs 500 to 1200 mm fails 142.

## The sheet

Look first at `fl-0-r-stair.png` (the 1961 panel, its edges and the moved risers), `fl-1-r-bank.png` (a bank face seen only from beyond 8 m, its footing stepping with the ground) and `steps-plan.png`.

- `fl-0-r-stair.png`
- `fl-0-r-bank.png`
- `fl-0-l-stair.png`
- `fl-0-l-bank.png`
- `fl-1-r-stair.png`
- `fl-1-r-bank.png`
- `fl-1-l-stair.png`
- `fl-1-l-bank.png`
- `fl-0-r-stair-1going.png`
- `fl-0-l-stair-1going.png`
- `fl-1-r-stair-1going.png`
- `fl-1-l-stair-1going.png`
- `steps-plan.png`
- `visibility.png`

Each elevation is drawn at 1:50 in strips of 6 m. Face stones are grey, the 1961 panel's are a warmer grey; throughs, head ties, runners, topstones and copings each have their own tone. A failing check is drawn in red, and a stone the fill laid with less of the rule in magenta. On the stair faces each fall point the facts give is ringed: orange where its stone fell (the hole is black), black where the facts hold it, grey where no stone could be chosen for it. The legend is on each sheet.

## What fails, and why

1. **One going a level run: 139 coping slabs under 450 mm.** A going here is 296 to 297 mm, so a level run of one going is about 300 mm long and holds no whole slab. The laying lays each such run as one slab of its own length (never under the working's least, 200 mm) and flags it: 139 of the one-going variant's 184 flags. SN2's test fails them. This is the nature of one going with this coping, not a fault to fix; it is why two goings are laid.
2. **The flags and cuts.** 10 flags: fl-0/r stair course 17: the tooth at 5664 is 117 mm off it, over 90; fl-0/l bank course 11: the tooth at 4041 is 121 mm off it, over 90; fl-1/r stair course 43: the tooth at 27872 is 124 mm off it, over 90; fl-1/r bank course 10: the tooth at 6742 is 122 mm off it, over 90; fl-1/l/hd-0/st-1: 193 mm, outside its range (220, 320), to leave whole stones beside it; fl-1/l stair course 43: the tooth at 27872 is 124 mm off it, over 90; fl-1/l bank course 6: the tooth at 3413 is 44 mm off it, under 50, to keep its laps; fl-1/l bank course 25: the tooth at 15913 is 119 mm off it, over 90; fl-1/l bank course 38: the tooth at 26232 is 116 mm off it, over 90; fl-1/l: the fallen stone at 27662 lies within 308 mm of a panel's boundary. 5 cuts: at each, a panel's boundary or the 1961 edge lies within one least stone (180 mm) of the course's end against the ground or a step, so no tooth fits. The course's end serves as the boundary's joint, and the stone there belongs to the panel that holds its middle. None breaks a check; each is listed under The laying's own reports.
3. **The steps' 9 mm of play (SN3).** The longest slab is 2300 mm and the stair 3512 mm across, ends in the walls. Its joint must then start in [-548, -540] or [536, 544] mm, outside the middle third (536 mm either side of the walking line): 9 mm of play a side. So every step's joint lies on one of two lines about a metre apart, alternating up the stair. Every SN3 check passes. Whether the two lines read as mechanical is a look question for R2b's grey sheet, not a rule's, and I propose no change without that evidence. A longer slab is the finish's fact, from `kinds/stair.json`.
4. **fl-1's rests.** 6 rests are 2960 to 3699 mm deep, more than the longest slab (2300), so each takes four slabs in two rows where the plan names two. SN3's "two to four slabs" passes. A rest's two slabs must also meet within 544 mm of the centre, inside the middle third. SN3 puts that rule on steps, so the rest joints are notes, not failures. No rule change: both follow from the plan's depths and the finish's sizes.

## Assumed

- **Houses are not occluders in the measurement,** since the brief names the terrain and the walls, and the clay's houses are blockouts that will move. A sensitivity adds them as boxes to their eaves: no faces change (The visibility measurement).
- **The eyes:** a standing eye at 1.6 m over every walkable lane, stair, quay, place and yard within 80 m, and the six judging views in their frames. A wall's occluding top is a slab 0.15 to 0.57 m outside the stair's clear half-width, up to its coping's top. L0's range is 8 m (SN8).
- **A sample is buried** where the ground 0.1 m outside the face stands over its mid-height. Buried stones are laid, because their face is seen.
- **Two goings** a level run is the variant laid and counted; one going is laid and tested beside it.
- **"A whole course a step"** (SN2) is read as a whole number of courses: with two goings and one course a rise, the coping steps by two courses (up to 356 mm). Read as exactly one course, SN2's own two-going option could not exist once a course is a rise. SN2's "an extra course goes in where a step would grow too big" gives no number, and no step here is more than two rises, so none goes in; R2b's grey form judges the steps' size.
- **A stepped section's corner stone** is at least 2 times its course's height (SN2 does not give a number).
- **The 1961 panel's edges** are straight joints through every course by the facts, exempt from SN10's laps and chains; its edge stones are long and short in alternate courses.
- **The foundation courses** under the foot hold no stones at R1, since no face reaches below the foot. Their lines are drawn from the largest down: each is at least the course over it (fixed this round, after the self-check found fl-0/r's at 194 under 252). SN10's test now checks every course above, as its rule says.
- **Seeds and rounding** as round 1: every draw keys on the pack's world seed through `HS.Stream`, `HS.h` and `HS.between`. The facts were rounded once to integer mm at the boundary. wall.py's own fact draws (the 1961 panel, the fall points, which falls cement holds) are at its seed 1, so R1 is re-run when they move into a wl-gully record.
- **`tools/check.py`** does not exist yet: it is built after the reset on 26 October. This run's own tests and `tools/validate_record.py` stand in for it.
- **Not laid at R1:** the coping's rebates and the batter (3D, R2); the patched holes; the 1952 campaign's reset run; the hidden work under the step ends and the stair's surface.

