# R1: the gully's walls and steps as elevations

Port step 2b, rung R1 (`reviews/lt1/port/2b/design.md`, The ladder). The cheek walls and the steps laid in integer millimetres by `blender/generators/masonry.py`, from `r1/facts.json`, checked and drawn by `tools/r1_elevations.py`. Numbers and faults only; no judgement of the look.

## Not done; next round

Stopped here for usage (the coordinator, 22 October). The design changed at e84862e after this run was built: dry lane walls carry no raked coping, so SN2 now has a retaining wall with no coping (the bank over a level top course) and a parapet with level slab copings stepped square, a whole course a step, nothing cut to a rake.

- **Stepped tops** replace this run's kneelers, knees, intermediate kneelers and raked copings (and the rake cuts under them); `masonry.py`'s `_coping` and the SN2 rake tests are to be redone, not finished.
- **The stone count:** 8,620 wall stones (8,301 face) against the design's about 2,700; L0 421,320 triangles against 150,000 (walls 370,320 against 110,000). Why: every rise (146 to 188 mm) is over the 140 mm course, so two courses a rise, median 83 mm; stones of 180 mm to 4.5 times that height are short; and both faces are laid stone by stone (the bank face alone is about 60% of the face stones, the walls' faces 212 m2 against 140).
- **Lap failures:** 18 laps and 5 four-stone crosses, all at the free lengths the fill relaxed (short runs in thin courses; What fails, 2).

**The coordinator's read (22 October, 22:20).** Not passed. The next round starts from three decisions.
- **One course a rise.** The 140 mm maximum course came from `wall.py`. The town's own walls (`docs/references/stone/` 31 and 36) are thick split slabs, so the course range rises to cover a rise (up to about 190 mm), with one course on each step top as SN2 already allows. That roughly halves the stone count.
- **The back faces.** All four walls are parapets (`retains: false` in the clay's ground), so both faces are seen from somewhere. Measure which back faces the five judging views and the walkable ground can see before deciding how they are laid.
- **The budget.** SN8's 110k for the walls assumed 140 m² of face, and the walls have 212.5 m². Re-derive it from the faces that are seen, then hold to it.

## In short

- **Hash:** `aec969068f3406f1` (laid twice in one run: the same); the run is repeated in a second process to show it holds.
- **Tests:** 37 checks; 34 pass, 3 fail (36 failures in all). The failures, each with its cause, are under Tests.
- **Counts (SN8):** 8620 wall stones (8301 face stones, 106 copings, 22 kneelers of which 4 intermediate, 18 knees, 71 throughs, 96 head stones, 6 topstones), 212.5 m2 of face on both faces, 170 step stones and slabs. L0 at the design's rates: walls 370,320 triangles against 110,000, stairs 51,000 against 40,000, the gully 421,320 against 150,000.
- **Joints through more than two courses, by cause:** 8 a tall stone's side (topstone); 5 course joints.
- **Panels re-lay alone:** 32 of 40 panels re-laid with an event's seed change no stone outside themselves; the worst changes 35 (wl-gully/fl-1/r/pn-11).

## Tests

| Rule | Check | Checked | Failed |
| --- | --- | --- | --- |
| SN1 | convex | 8620 | 0 |
| SN1 | integer outlines | 8620 | 0 |
| SN10 | laps | 8144 | 18 |
| SN10 | line of minimum trace | 0 | 0 |
| SN10 | no four-stone cross | 8131 | 5 |
| SN10 | no joint through more than two courses | 8139 | 13 |
| SN10 | no stone over 4.5 x its height | 8468 | 0 |
| SN10 | the largest courses low | 221 | 0 |
| SN2 | a knee at every downward break | 18 | 0 |
| SN2 | a kneeler at every upward break | 18 | 0 |
| SN2 | a line on each step top | 160 | 0 |
| SN2 | at most one line between step tops | 156 | 0 |
| SN2 | bank footing in whole courses | 259 | 0 |
| SN2 | course heights 60 to 140 | 393 | 0 |
| SN2 | every course ends at a footing or the coping | 1516 | 0 |
| SN2 | heads: ties and runners alternate | 8 | 0 |
| SN2 | intermediate kneelers every 2.4 to 3.6 m | 26 | 0 |
| SN2 | kneelers wider than high | 22 | 0 |
| SN2 | level beds on course lines | 8514 | 0 |
| SN2 | no angle under 25 degrees | 8620 | 0 |
| SN2 | no face under 50 mm | 8620 | 0 |
| SN2 | no stone under 50 mm high | 8468 | 0 |
| SN2 | rake cuts leave trapezoids | 532 | 0 |
| SN2 | square topstones | 6 | 0 |
| SN3 | ends 150 mm into the walls | 81 | 0 |
| SN3 | joint outside the middle third | 71 | 0 |
| SN3 | joints alternate | 69 | 0 |
| SN3 | laps 40 to 60 mm | 77 | 0 |
| SN3 | never pieced in depth | 71 | 0 |
| SN3 | no joint within 150 mm of the one below | 83 | 0 |
| SN3 | one or two stones a step | 71 | 0 |
| SN3 | rests: two to four slabs | 8 | 0 |
| SN3 | within the finish's sizes | 170 | 0 |
| SN4 | 4 to 7 edges | 8620 | 0 |
| SN5 | tread joints 4 to 10 mm | 85 | 0 |
| ids | ids are unique | 1 | 0 |
| ids | ids follow the grammar | 8790 | 0 |

**SN10, laps.** 

- FAIL wl-gully/fl-0/r stair course 35 at 5544: 30 mm from the joint below at 5574 (lap 40); where the fill was relaxed: wl-gully/fl-0/r/pn-3/stair/co-34/sp-0 bond below only; wl-gully/fl-0/r/pn-3/stair/co-34/sp-1 bond below only
- FAIL wl-gully/fl-0/r stair course 72 at 9817: 1 mm from the joint below at 9818 (lap 40); where the fill was relaxed: wl-gully/fl-0/r/pn-4/stair/co-72/sp-0 no bond; wl-gully/fl-0/r/pn-4/stair/co-72/sp-1 no bond
- FAIL wl-gully/fl-0/r bank course 68 at 10034: 14 mm from the joint below at 10048 (lap 40); where the fill was relaxed: wl-gully/fl-0/r/pn-5/bank/co-67/sp-0 bond below only; wl-gully/fl-0/r/pn-5/bank/co-67/sp-1 bond below only
- FAIL wl-gully/fl-1/r stair course 20 at 6480: 36 mm from the joint below at 6516 (lap 40); where the fill was relaxed: wl-gully/fl-1/r/pn-3/stair/co-19/sp-0 bond below only; wl-gully/fl-1/r/pn-3/stair/co-19/sp-1 bond below only
- FAIL wl-gully/fl-1/r stair course 34 at 11313: 33 mm from the joint below at 11280 (lap 40); where the fill was relaxed: wl-gully/fl-1/r/pn-5/stair/co-34/sp-0 no bond; wl-gully/fl-1/r/pn-5/stair/co-34/sp-1 no bond
- FAIL wl-gully/fl-1/r stair course 105 at 32878: 36 mm from the joint below at 32842 (lap 40); where the fill was relaxed: wl-gully/fl-1/r/pn-13/stair/co-105/sp-0 no bond; wl-gully/fl-1/r/pn-13/stair/co-105/sp-1 no bond
- FAIL wl-gully/fl-1/r bank course 5 at 309: 11 mm from the joint below at 320 (lap 40); where the fill was relaxed: wl-gully/fl-1/r/pn-0/bank/co-4/sp-1 bond below only; wl-gully/fl-1/r/pn-0/bank/co-4/sp-2 bond below only
- FAIL wl-gully/fl-1/r bank course 81 at 22900: 6 mm from the joint below at 22894 (lap 48); where the fill was relaxed: wl-gully/fl-1/r/pn-10/bank/co-80/sp-0 bond below only; wl-gully/fl-1/r/pn-10/bank/co-80/sp-1 bond below only
- FAIL wl-gully/fl-1/r bank course 81 at 25507: 7 mm from the joint below at 25514 (lap 48); where the fill was relaxed: wl-gully/fl-1/r/pn-10/bank/co-80/sp-11 bond below only; wl-gully/fl-1/r/pn-10/bank/co-80/sp-12 bond below only
- FAIL wl-gully/fl-1/r bank course 81 at 25946: 43 mm from the joint below at 25989 (lap 48); where the fill was relaxed: wl-gully/fl-1/r/pn-10/bank/co-80/sp-13 bond below only; wl-gully/fl-1/r/pn-10/bank/co-80/sp-14 bond below only
- FAIL wl-gully/fl-1/l stair course 4 at 1420: 35 mm from the joint below at 1385 (lap 40); where the fill was relaxed: wl-gully/fl-1/l/pn-1/stair/co-4/sp-0 no bond; wl-gully/fl-1/l/pn-1/stair/co-4/sp-1 no bond
- FAIL wl-gully/fl-1/l stair course 26 at 3433: 28 mm from the joint below at 3461 (lap 40); where the fill was relaxed: wl-gully/fl-1/l/pn-1/stair/co-26/sp-0 no bond; wl-gully/fl-1/l/pn-1/stair/co-26/sp-1 no bond
- FAIL wl-gully/fl-1/l stair course 58 at 20438: 28 mm from the joint below at 20410 (lap 40); where the fill was relaxed: wl-gully/fl-1/l/pn-9/stair/co-58/sp-0 no bond; wl-gully/fl-1/l/pn-9/stair/co-58/sp-1 no bond
- FAIL wl-gully/fl-1/l stair course 62 at 18498: 33 mm from the joint below at 18465 (lap 40); where the fill was relaxed: wl-gully/fl-1/l/pn-8/stair/co-62/sp-3 no bond; wl-gully/fl-1/l/pn-8/stair/co-62/sp-4 no bond
- FAIL wl-gully/fl-1/l stair course 86 at 27690: 32 mm from the joint below at 27722 (lap 40); where the fill was relaxed: wl-gully/fl-1/l/pn-11/stair/co-86/sp-3 no bond; wl-gully/fl-1/l/pn-11/stair/co-86/sp-4 no bond
- FAIL wl-gully/fl-1/l bank course 63 at 20396: 24 mm from the joint below at 20420 (lap 40); where the fill was relaxed: wl-gully/fl-1/l/pn-9/bank/co-62/sp-0 bond below only; wl-gully/fl-1/l/pn-9/bank/co-62/sp-1 bond below only
- FAIL wl-gully/fl-1/l bank course 91 at 31396: 24 mm from the joint below at 31420 (lap 42); where the fill was relaxed: wl-gully/fl-1/l/pn-13/bank/co-90/sp-0 bond below only; wl-gully/fl-1/l/pn-13/bank/co-90/sp-1 bond below only
- FAIL wl-gully/fl-1/l bank course 107 at 33106: 12 mm from the joint below at 33118 (lap 40); where the fill was relaxed: wl-gully/fl-1/l/pn-14/bank/co-107/sp-0 no bond; wl-gully/fl-1/l/pn-14/bank/co-107/sp-1 no bond
- wl-gully/fl-0/r stair course 18: the 1961 edge's straight joint at 1844 (a fact, exempt)
- wl-gully/fl-0/r stair course 19: the 1961 edge's straight joint at 1844 (a fact, exempt)
- wl-gully/fl-0/r stair course 20: the 1961 edge's straight joint at 1844 (a fact, exempt)
- wl-gully/fl-0/r stair course 21: the 1961 edge's straight joint at 1844 (a fact, exempt)
- wl-gully/fl-0/r stair course 22: the 1961 edge's straight joint at 1844 (a fact, exempt)
- wl-gully/fl-0/r stair course 23: the 1961 edge's straight joint at 1844 (a fact, exempt)
- wl-gully/fl-0/r stair course 24: the 1961 edge's straight joint at 1844 (a fact, exempt)
- wl-gully/fl-0/r stair course 25: the 1961 edge's straight joint at 1844 (a fact, exempt)
- wl-gully/fl-0/r stair course 40: the 1961 edge's straight joint at 6226 (a fact, exempt)
- wl-gully/fl-0/r stair course 41: the 1961 edge's straight joint at 6226 (a fact, exempt)
- wl-gully/fl-0/r stair course 42: the 1961 edge's straight joint at 6226 (a fact, exempt)
- wl-gully/fl-0/r stair course 43: the 1961 edge's straight joint at 6226 (a fact, exempt)
- wl-gully/fl-0/r stair course 44: the 1961 edge's straight joint at 6226 (a fact, exempt)
- wl-gully/fl-0/r stair course 45: the 1961 edge's straight joint at 6226 (a fact, exempt)
- wl-gully/fl-0/r stair course 46: the 1961 edge's straight joint at 6226 (a fact, exempt)
- wl-gully/fl-0/r bank course 11: the 1961 edge's straight joint at 1844 (a fact, exempt)
- wl-gully/fl-0/r bank course 12: the 1961 edge's straight joint at 1844 (a fact, exempt)
- wl-gully/fl-0/r bank course 13: the 1961 edge's straight joint at 1844 (a fact, exempt)
- wl-gully/fl-0/r bank course 14: the 1961 edge's straight joint at 1844 (a fact, exempt)
- wl-gully/fl-0/r bank course 15: the 1961 edge's straight joint at 1844 (a fact, exempt)
- wl-gully/fl-0/r bank course 16: the 1961 edge's straight joint at 1844 (a fact, exempt)
- wl-gully/fl-0/r bank course 17: the 1961 edge's straight joint at 1844 (a fact, exempt)
- wl-gully/fl-0/r bank course 18: the 1961 edge's straight joint at 1844 (a fact, exempt)
- wl-gully/fl-0/r bank course 19: the 1961 edge's straight joint at 1844 (a fact, exempt)
- wl-gully/fl-0/r bank course 20: the 1961 edge's straight joint at 1844 (a fact, exempt)
- wl-gully/fl-0/r bank course 21: the 1961 edge's straight joint at 1844 (a fact, exempt)
- wl-gully/fl-0/r bank course 22: the 1961 edge's straight joint at 1844 (a fact, exempt)
- wl-gully/fl-0/r bank course 23: the 1961 edge's straight joint at 1844 (a fact, exempt)
- wl-gully/fl-0/r bank course 24: the 1961 edge's straight joint at 1844 (a fact, exempt)
- wl-gully/fl-0/r bank course 25: the 1961 edge's straight joint at 1844 (a fact, exempt)
- wl-gully/fl-0/r bank course 25: the 1961 edge's straight joint at 6226 (a fact, exempt)
- wl-gully/fl-0/r bank course 26: the 1961 edge's straight joint at 6226 (a fact, exempt)
- wl-gully/fl-0/r bank course 27: the 1961 edge's straight joint at 6226 (a fact, exempt)
- wl-gully/fl-0/r bank course 28: the 1961 edge's straight joint at 6226 (a fact, exempt)
- wl-gully/fl-0/r bank course 29: the 1961 edge's straight joint at 6226 (a fact, exempt)
- wl-gully/fl-0/r bank course 30: the 1961 edge's straight joint at 6226 (a fact, exempt)
- wl-gully/fl-0/r bank course 31: the 1961 edge's straight joint at 6226 (a fact, exempt)
- wl-gully/fl-0/r bank course 32: the 1961 edge's straight joint at 6226 (a fact, exempt)
- wl-gully/fl-0/r bank course 33: the 1961 edge's straight joint at 6226 (a fact, exempt)
- wl-gully/fl-0/r bank course 34: the 1961 edge's straight joint at 6226 (a fact, exempt)
- ... and 12 more notes

**SN10, line of minimum trace.** reported per wall panel

- wl-gully/fl-0/r/pn-0 stair: 1.99 times the height over courses 5 to 25 (1751 mm; 1.00 is a straight joint)
- wl-gully/fl-0/r/pn-1 stair: 2.12 times the height over courses 17 to 40 (2016 mm; 1.00 is a straight joint)
- wl-gully/fl-0/r/pn-2 stair: 1.70 times the height over courses 33 to 42 (816 mm; 1.00 is a straight joint)
- wl-gully/fl-0/r/pn-3 stair: 1.67 times the height over courses 33 to 46 (1151 mm; 1.00 is a straight joint)
- wl-gully/fl-0/r/pn-4 stair: 2.32 times the height over courses 39 to 73 (2742 mm; 1.00 is a straight joint)
- wl-gully/fl-0/r/pn-5 stair: 1.84 times the height over courses 66 to 76 (663 mm; 1.00 is a straight joint)
- wl-gully/fl-0/r/pn-0 bank: 1.96 times the height over courses 3 to 25 (1912 mm; 1.00 is a straight joint)
- wl-gully/fl-0/r/pn-1 bank: 1.88 times the height over courses 10 to 40 (2568 mm; 1.00 is a straight joint)
- wl-gully/fl-0/r/pn-2 bank: 1.82 times the height over courses 17 to 42 (2162 mm; 1.00 is a straight joint)
- wl-gully/fl-0/r/pn-3 bank: 1.28 times the height over courses 22 to 46 (2057 mm; 1.00 is a straight joint)
- wl-gully/fl-0/r/pn-4 bank: 1.93 times the height over courses 24 to 73 (3982 mm; 1.00 is a straight joint)
- wl-gully/fl-0/r/pn-5 bank: 2.05 times the height over courses 37 to 76 (3088 mm; 1.00 is a straight joint)
- wl-gully/fl-0/l/pn-0 stair: 2.39 times the height over courses 5 to 40 (3015 mm; 1.00 is a straight joint)
- wl-gully/fl-0/l/pn-1 stair: 1.80 times the height over courses 33 to 42 (816 mm; 1.00 is a straight joint)
- wl-gully/fl-0/l/pn-2 stair: 2.42 times the height over courses 34 to 69 (3131 mm; 1.00 is a straight joint)
- wl-gully/fl-0/l/pn-3 stair: 1.99 times the height over courses 63 to 72 (927 mm; 1.00 is a straight joint)
- wl-gully/fl-0/l/pn-0 bank: 2.25 times the height over courses 3 to 40 (3176 mm; 1.00 is a straight joint)
- wl-gully/fl-0/l/pn-1 bank: 1.88 times the height over courses 16 to 42 (2243 mm; 1.00 is a straight joint)
- wl-gully/fl-0/l/pn-2 bank: 2.18 times the height over courses 20 to 69 (4292 mm; 1.00 is a straight joint)
- wl-gully/fl-0/l/pn-3 bank: 1.72 times the height over courses 54 to 72 (1676 mm; 1.00 is a straight joint)
- wl-gully/fl-1/r/pn-0 stair: 1.63 times the height over courses 3 to 12 (829 mm; 1.00 is a straight joint)
- wl-gully/fl-1/r/pn-1 stair: 2.21 times the height over courses 4 to 26 (1883 mm; 1.00 is a straight joint)
- wl-gully/fl-1/r/pn-2 stair: 1.61 times the height over courses 19 to 28 (836 mm; 1.00 is a straight joint)
- wl-gully/fl-1/r/pn-3 stair: 2.14 times the height over courses 19 to 40 (1814 mm; 1.00 is a straight joint)
- wl-gully/fl-1/r/pn-4 stair: 1.71 times the height over courses 33 to 42 (818 mm; 1.00 is a straight joint)
- wl-gully/fl-1/r/pn-5 stair: 2.13 times the height over courses 33 to 52 (1663 mm; 1.00 is a straight joint)
- wl-gully/fl-1/r/pn-6 stair: 1.59 times the height over courses 45 to 54 (833 mm; 1.00 is a straight joint)
- wl-gully/fl-1/r/pn-7 stair: 2.21 times the height over courses 45 to 64 (1675 mm; 1.00 is a straight joint)
- wl-gully/fl-1/r/pn-8 stair: 1.62 times the height over courses 57 to 66 (835 mm; 1.00 is a straight joint)
- wl-gully/fl-1/r/pn-9 stair: 2.26 times the height over courses 57 to 80 (1990 mm; 1.00 is a straight joint)
- wl-gully/fl-1/r/pn-10 stair: 1.66 times the height over courses 73 to 82 (834 mm; 1.00 is a straight joint)
- wl-gully/fl-1/r/pn-11 stair: 2.21 times the height over courses 73 to 94 (1828 mm; 1.00 is a straight joint)
- wl-gully/fl-1/r/pn-12 stair: 1.66 times the height over courses 87 to 96 (849 mm; 1.00 is a straight joint)
- wl-gully/fl-1/r/pn-13 stair: 2.17 times the height over courses 87 to 106 (1683 mm; 1.00 is a straight joint)
- wl-gully/fl-1/r/pn-14 stair: 1.68 times the height over courses 99 to 109 (855 mm; 1.00 is a straight joint)
- wl-gully/fl-1/r/pn-0 bank: 1.91 times the height over courses 3 to 12 (829 mm; 1.00 is a straight joint)
- wl-gully/fl-1/r/pn-1 bank: 2.36 times the height over courses 8 to 26 (1566 mm; 1.00 is a straight joint)
- wl-gully/fl-1/r/pn-2 bank: 2.00 times the height over courses 12 to 28 (1410 mm; 1.00 is a straight joint)
- wl-gully/fl-1/r/pn-3 bank: 2.17 times the height over courses 20 to 40 (1738 mm; 1.00 is a straight joint)
- wl-gully/fl-1/r/pn-4 bank: 1.68 times the height over courses 26 to 42 (1408 mm; 1.00 is a straight joint)
- ... and 40 more notes

**SN10, no four-stone cross.** no four stones meeting at a point

- FAIL wl-gully/fl-0/r stair course 72 at 9817: wl-gully/fl-0/r/pn-4/stair/co-72/sp-0, wl-gully/fl-0/r/pn-4/stair/co-72/sp-1 over wl-gully/fl-0/r/pn-4/stair/co-71/sp-1, wl-gully/fl-0/r/pn-5/stair/co-71/sp-0
- FAIL wl-gully/fl-1/r bank course 5 at 309: wl-gully/fl-1/r/hd-0/st-1/bank, wl-gully/fl-1/r/pn-0/bank/co-5/sp-0 over wl-gully/fl-1/r/pn-0/bank/co-4/sp-1, wl-gully/fl-1/r/pn-0/bank/co-4/sp-2
- FAIL wl-gully/fl-1/r bank course 81 at 22900: wl-gully/fl-1/r/knee-4, wl-gully/fl-1/r/pn-10/bank/co-81/sp-0 over wl-gully/fl-1/r/pn-10/bank/co-80/sp-0, wl-gully/fl-1/r/pn-10/bank/co-80/sp-1
- FAIL wl-gully/fl-1/r bank course 81 at 25507: wl-gully/fl-1/r/pn-10/bank/co-81/sp-7, wl-gully/fl-1/r/kneeler-5 over wl-gully/fl-1/r/pn-10/bank/co-80/sp-11, wl-gully/fl-1/r/pn-10/bank/co-80/sp-12
- FAIL wl-gully/fl-1/l bank course 107 at 33106: wl-gully/fl-1/l/pn-14/bank/co-107/sp-0, wl-gully/fl-1/l/pn-14/bank/co-107/sp-1 over wl-gully/fl-1/l/pn-13/bank/co-106/sp-1, wl-gully/fl-1/l/pn-13/bank/co-106/sp-2

**SN10, no joint through more than two courses.** no vertical joint through more than two courses

- FAIL wl-gully/fl-0/r stair courses 74 to 76 at 10258: a joint through 3 courses: the plumb side of wl-gully/fl-0/r/hd-1/top (topstone, 3 courses high)
- FAIL wl-gully/fl-0/r bank courses 67 to 69 at 10034: a joint through 3 courses: joints of course stones in line; relaxed: bond below only
- FAIL wl-gully/fl-0/r bank courses 74 to 76 at 10258: a joint through 3 courses: the plumb side of wl-gully/fl-0/r/hd-1/top (topstone, 3 courses high)
- FAIL wl-gully/fl-0/l stair courses 70 to 72 at 10247: a joint through 3 courses: the plumb side of wl-gully/fl-0/l/hd-1/top (topstone, 3 courses high)
- FAIL wl-gully/fl-0/l bank courses 70 to 72 at 10247: a joint through 3 courses: the plumb side of wl-gully/fl-0/l/hd-1/top (topstone, 3 courses high)
- FAIL wl-gully/fl-1/r stair courses 107 to 109 at 33427: a joint through 3 courses: the plumb side of wl-gully/fl-1/r/hd-1/top (topstone, 3 courses high)
- FAIL wl-gully/fl-1/r bank courses 4 to 6 at 309: a joint through 3 courses: joints of course stones in line; relaxed: bond below only
- FAIL wl-gully/fl-1/r bank courses 80 to 82 at 22894: a joint through 3 courses: joints of course stones in line; relaxed: bond below only
- FAIL wl-gully/fl-1/r bank courses 80 to 82 at 25507: a joint through 3 courses: joints of course stones in line; relaxed: bond below only
- FAIL wl-gully/fl-1/r bank courses 80 to 82 at 25946: a joint through 3 courses: joints of course stones in line; relaxed: bond below only
- FAIL wl-gully/fl-1/r bank courses 107 to 109 at 33427: a joint through 3 courses: the plumb side of wl-gully/fl-1/r/hd-1/top (topstone, 3 courses high)
- FAIL wl-gully/fl-1/l stair courses 105 to 110 at 33374: a joint through 6 courses: the plumb side of wl-gully/fl-1/l/hd-1/top (topstone, 6 courses high)
- FAIL wl-gully/fl-1/l bank courses 105 to 110 at 33374: a joint through 6 courses: the plumb side of wl-gully/fl-1/l/hd-1/top (topstone, 6 courses high); relaxed: no bond
- wl-gully/fl-0/r stair: the longest run of joints within a lap of each other spans 9 courses (a two-course head's side counts as two)
- wl-gully/fl-0/r bank: the longest run of joints within a lap of each other spans 23 courses (a two-course head's side counts as two)
- wl-gully/fl-0/l stair: the longest run of joints within a lap of each other spans 3 courses (a two-course head's side counts as two)
- wl-gully/fl-0/l bank: the longest run of joints within a lap of each other spans 3 courses (a two-course head's side counts as two)
- wl-gully/fl-1/r stair: the longest run of joints within a lap of each other spans 3 courses (a two-course head's side counts as two)
- wl-gully/fl-1/r bank: the longest run of joints within a lap of each other spans 3 courses (a two-course head's side counts as two)
- wl-gully/fl-1/l stair: the longest run of joints within a lap of each other spans 6 courses (a two-course head's side counts as two)
- wl-gully/fl-1/l bank: the longest run of joints within a lap of each other spans 6 courses (a two-course head's side counts as two)

**SN2, bank footing in whole courses.** on the bank side the footing steps with the ground, each step a whole course

- wl-gully/fl-0/r: 36 footing steps, the shortest inner tread 300 mm
- wl-gully/fl-0/l: 34 footing steps, the shortest inner tread 300 mm
- wl-gully/fl-1/r: 93 footing steps, the shortest inner tread 300 mm
- wl-gully/fl-1/l: 96 footing steps, the shortest inner tread 300 mm

**SN2, every course ends at a footing or the coping.** each course starts on the footing uphill and ends under the coping downhill (or at the wall's head)

- wl-gully/fl-0/r: course ends by kind {'end': 67, 'feature': 24, 'ground': 35, 'rake': 106, 'step': 60}
- wl-gully/fl-0/l: course ends by kind {'end': 63, 'feature': 24, 'ground': 33, 'rake': 96, 'step': 60}
- wl-gully/fl-1/r: course ends by kind {'end': 36, 'feature': 84, 'ground': 92, 'rake': 164, 'step': 96}
- wl-gully/fl-1/l: course ends by kind {'end': 29, 'feature': 90, 'ground': 95, 'rake': 166, 'step': 96}

**SN2, rake cuts leave trapezoids.** 

- wl-gully/fl-0/r: 106 stones cut by the rake, 106 trapezoids and 0 pentagons; their shortest edge 50 mm, their most acute corner 29.2 degrees
- wl-gully/fl-0/l: 96 stones cut by the rake, 96 trapezoids and 0 pentagons; their shortest edge 50 mm, their most acute corner 28.8 degrees
- wl-gully/fl-1/r: 164 stones cut by the rake, 164 trapezoids and 0 pentagons; their shortest edge 50 mm, their most acute corner 28.4 degrees
- wl-gully/fl-1/l: 166 stones cut by the rake, 166 trapezoids and 0 pentagons; their shortest edge 50 mm, their most acute corner 28.3 degrees

**SN3, joint outside the middle third.** the joint falls outside the walking line's middle third (|x| >= 536 mm)

- st-gully/fl-0/tr-14 row [4153, 5799]: a rest's joint at 386 lies inside the middle third (two slabs of at most 2300 across 3512 mm must meet within 544 mm of the centre; SN3 puts the rule on steps)
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

| Wall line | Stones | By kind | Face m2 (stair, bank) | L0 triangles |
| --- | --- | --- | --- | --- |
| wl-gully/fl-0/r | 1407 | coping 12, face 1346, face (bank) 937, face (stair) 409, head runner 22, head tie 12, knee 2, kneeler 4, through 8, topstone 1 | 11.28, 23.12 | 61,160 |
| wl-gully/fl-0/l | 1438 | coping 13, face 1374, face (bank) 986, face (stair) 388, head runner 24, head tie 11, knee 2, kneeler 4, through 9, topstone 1 | 11.48, 24.57 | 62,640 |
| wl-gully/fl-1/r | 3086 | coping 41, face 2987, face (bank) 1747, face (stair) 1240, head runner 10, head tie 5, knee 7, kneeler 7, through 27, topstone 2 | 32.41, 43.3 | 131,360 |
| wl-gully/fl-1/l | 2689 | coping 40, face 2594, face (bank) 1348, face (stair) 1246, head runner 8, head tie 4, knee 7, kneeler 7, through 27, topstone 2 | 32.12, 34.17 | 115,160 |
| st-gully/fl-0 (steps) | 60 | step 58, rest 2 | | 18,000 |
| st-gully/fl-1 (steps) | 110 | landing 2, step 84, rest 24 | | 33,000 |

The design's estimate was about 2,700 wall stones, 140 m2 of face and 150 copings.

## The laying's own reports

**wl-gully/fl-0/r.**
- fall at s 7344, z 7329: fell: course 55, 7281 to 7625
- free lengths laid without the full rule: 2 bond below only, 7 bond, the 1961 long-and-short end dropped, 1 no bond
- boundaries that took no tooth or straight joint in a course: 25
- wl-gully/fl-0/r/knee-1: its plumb side rises through 4 courses
- wl-gully/fl-0/r/hd-0/st-0: 300 mm, outside its range (180, 260), to leave whole stones beside it

**wl-gully/fl-0/l.**
- fall at s 7649, z 6886: held (cement: the 1961 panel or the patched hole)
- fall at s 2366, z 4877: fell: course 25, 2205 to 2462
- boundaries that took no tooth or straight joint in a course: 14
- wl-gully/fl-0/l/knee-1: its plumb side rises through 3 courses
- wl-gully/fl-0/l/hd-0/st-0: 300 mm, outside its range (180, 260), to leave whole stones beside it
- wl-gully/fl-0/l/hd-0/st-1/stair: no length leaves whole stones beside it (rooms [(300, 68), (597, 99)]); 300 mm
- wl-gully/fl-0/l/hd-0/st-1/stair: a runner 300 mm, under the 400 a runner should be

**wl-gully/fl-1/r.**
- fall at s 596, z 8643: fell: course 10, 488 to 733
- fall at s 5953, z 10005: fell: course 27, 5774 to 6119
- fall at s 2867, z 9237: fell: course 17, 2717 to 2995
- free lengths laid without the full rule: 3 bond below only, 2 no bond
- through stones not placed: 2 (10754, 12584)
- boundaries that took no tooth or straight joint in a course: 19
- wl-gully/fl-1/r/knee-6: its plumb side rises through 4 courses

**wl-gully/fl-1/l.**
- fall at s 32785, z 16510: fell: course 104, 32685 to 32943
- fall at s 27662, z 15598: fell: course 94, 27572 to 27884
- free lengths laid without the full rule: 2 bond below only, 6 no bond
- through stones not placed: 4 (6049, 12665, 31768, 32692)
- boundaries that took no tooth or straight joint in a course: 17
- wl-gully/fl-1/l/knee-6: its plumb side rises through 3 courses

## Panels re-laid one at a time

- wl-gully/fl-1/r/pn-8: 271 of its stones change and 4 outside it (e.g. wl-gully/fl-1/r/pn-9/stair/co-65/sp-0, wl-gully/fl-1/r/pn-9/stair/co-65/sp-1, wl-gully/fl-1/r/pn-9/stair/co-65/sp-2)
- wl-gully/fl-1/r/pn-9: 230 of its stones change and 5 outside it (e.g. wl-gully/fl-1/r/pn-8/bank/co-64/sp-11, wl-gully/fl-1/r/pn-8/bank/co-64/sp-12, wl-gully/fl-1/r/pn-8/bank/co-64/sp-13)
- wl-gully/fl-1/r/pn-11: 209 of its stones change and 35 outside it (e.g. wl-gully/fl-1/r/pn-10/bank/co-80/sp-0, wl-gully/fl-1/r/pn-10/bank/co-80/sp-1, wl-gully/fl-1/r/pn-10/bank/co-80/sp-10)
- wl-gully/fl-1/r/pn-14: 9 of its stones change and 5 outside it (e.g. wl-gully/fl-1/r/pn-13/stair/co-102/sp-2, wl-gully/fl-1/r/pn-13/stair/co-102/sp-3, wl-gully/fl-1/r/pn-13/stair/co-102/sp-4)
- wl-gully/fl-1/l/pn-3: 187 of its stones change and 7 outside it (e.g. wl-gully/fl-1/l/pn-2/bank/co-26/sp-10, wl-gully/fl-1/l/pn-2/bank/co-26/sp-11, wl-gully/fl-1/l/pn-2/bank/co-26/sp-12)
- wl-gully/fl-1/l/pn-5: 145 of its stones change and 6 outside it (e.g. wl-gully/fl-1/l/pn-4/bank/co-40/sp-10, wl-gully/fl-1/l/pn-4/bank/co-40/sp-11, wl-gully/fl-1/l/pn-4/stair/co-40/sp-10)
- wl-gully/fl-1/l/pn-11: 194 of its stones change and 3 outside it (e.g. wl-gully/fl-1/l/pn-12/stair/co-93/sp-0, wl-gully/fl-1/l/pn-12/stair/co-93/sp-1, wl-gully/fl-1/l/pn-12/stair/co-94/sp-0)
- wl-gully/fl-1/l/pn-14: 9 of its stones change and 2 outside it (e.g. wl-gully/fl-1/l/pn-13/stair/co-102/sp-3, wl-gully/fl-1/l/pn-13/stair/co-102/sp-4)
- the others (32) change only their own stones

## The sheet

- `fl-0-r-stair.png`
- `fl-0-r-bank.png`
- `fl-0-l-stair.png`
- `fl-0-l-bank.png`
- `fl-1-r-stair.png`
- `fl-1-r-bank.png`
- `fl-1-l-stair.png`
- `fl-1-l-bank.png`
- `steps-plan.png`

## What fails, and why

1. **Thin courses, the root of most of what follows.** Every rise is 146 to 188 mm, over wall.py's 140 mm course, so SN2's lines (one on each step top, at most one between) give two courses a rise: courses under the last step are 60 to 140 mm (median 83), the free courses above it 60 to 123 mm, falling upwards (the largest courses low). A stone is 180 mm to 4.5 times its height, so most are short: 8,301 face stones against the design's about 2,700, and the walls' L0 is 370,320 triangles against SN8's 110,000 (the gully 421,320 against 150,000). Undecided, not mine to decide: a course up to the largest rise (one course a rise, about a third of the stones), or the count kept and SN8's rates or budget changed.
2. **SN10 laps (18) and four-stone crosses (5), and 5 joints through three courses**, all at the 16 free lengths the fill could not lay in whole stones clear of the joints below and above, so laid with less of the rule (marked magenta on the sheet; each is listed under The laying's own reports). They are runs of 360 to 3586 mm in courses 60 to 76 mm high, between a panel's tooth, a step end, a stone laid first or the rake: one or two joints fit at all, and the course below has a joint there. The teeth are chosen before the fill, from the boundary alone, so that a panel re-lays alone; choosing them from the fill below would couple panels. Larger courses (1) would remove most of these.
3. **SN10 joints through more than two courses at the wall ends' topstones (8).** SN2's square topstone (220 to 450 mm, length 0.75 to 1.33 its height) at a flight's top end stands in the free courses of 60 to about 80 mm, so its plumb side passes through three courses or more (185, 193, 209, 242, 360 mm high). At wl-gully/fl-1/l the knee's level top (at most 350 mm, my own range) leaves the topstone too long to be square on the knee's bed, so its bed drops a further three courses. Undecided: a smaller topstone, larger free courses, or a topstone's side read as one stone's side rather than a joint through courses.
4. **Panels re-laid alone: 32 of 40.** The other 8 change 2 to 35 stones beyond themselves, nearly all in courses where a boundary took no tooth (the reports' 'boundaries that took no tooth': 75 course crossings in all), so one stone crosses it and is laid by the panel holding its middle; one or two follow a fallen stone redrawn near a boundary.
5. **Steps: L0 51,000 triangles against 40,000** (170 stones and slabs at 300). Every step test passes, but SN3's middle third leaves almost no room: with the finish's longest slab (2300 mm) across 3512 mm, a step's joint can only fall 536 to 544 mm from the centre (9 mm of play). A rest's two slabs must meet within 544 mm of the centre, so every rest joint is inside the middle third (SN3 puts the rule on steps; reported as notes). The plan names two slabs a rest; fl-1's rests are deeper than the longest slab and take four in two rows.

## Assumed, and not laid at R1

- **Seeds:** every new draw keys on the pack's world seed (1989) through `HS.Stream`/`HS.h`. The stair's plan is today's set-out from the record's kind at its legacySeed (1) and wall.py's own fact draws (the 1961 panel, the fall points and which are held by cement) are at its seed 1: R1 must be re-run when 2b retires legacySeed and when those facts move into a wl-gully record.
- **Rounding:** the stages' metres were rounded once to integer mm in `facts.json` (half away from zero) and nowhere after. The plan's S and D were rounded apart and differ by 1 mm in places; a step's depth is taken from the nosings (S), so each lap is exactly its drawn lap.
- **Steps:** laps 40 to 60 mm by SN3 (the kind's own lap is 100 mm); the middle third on the clear width between the walls' faces with their 6 mm joints (3212 mm, so |x| at least 536); ends 1756 mm from the centre (150 mm into each wall); the turn landing at fl-1's foot one rise thick, from the landing's front to the first step's nosing plus its lap.
- **Kneelers:** 'wider than high' is taken on the whole stone, bed to top; a kneeler's height is drawn near three quarters of its width, its plumb back through at most two courses where the lines allow; intermediate kneelers every 2.4 to 3.6 m of going (fl-1's raked runs are all under 2.4 m, so only fl-0 has them).
- **Not laid at R1:** the coping's rebates (a 3D matter, R2); the patched holes; the 1952 campaign's reset run (the plan's output does not say which steps it moved, so it is untested); the wall's hidden work under the step ends and under the stair's surface (veiled on the sheet); the batter (in the face alone, a 3D matter).
- **The laying's flags:** wl-gully/fl-0/r/knee-1: its plumb side rises through 4 courses; wl-gully/fl-0/r/hd-0/st-0: 300 mm, outside its range (180, 260), to leave whole stones beside it; wl-gully/fl-0/l/knee-1: its plumb side rises through 3 courses; wl-gully/fl-0/l/hd-0/st-0: 300 mm, outside its range (180, 260), to leave whole stones beside it; wl-gully/fl-0/l/hd-0/st-1/stair: no length leaves whole stones beside it (rooms [(300, 68), (597, 99)]); 300 mm; wl-gully/fl-0/l/hd-0/st-1/stair: a runner 300 mm, under the 400 a runner should be; wl-gully/fl-1/r/knee-6: its plumb side rises through 4 courses; wl-gully/fl-1/l/knee-6: its plumb side rises through 3 courses.
