# Pre-mortem: the gully's stone, redrawn to 2b's design

A fresh reviewer, 22 October 2026, from the lean packet only (design.md, stone.md's craft section, Q12 to Q15, the four tests, the eye-on crop, the target frame; greps of the generators and `Stone.shader`). Six months on, the redraw has failed. These are the ways it did.

## The failure stories

**1. Mason-true, screen-false.** The design spends most of its words on what a mason checks (level beds, kneelers, laps, bond numbers) and almost none on what the camera sees. At street, into12 and high a wall stone is 4 to 13 px high and its joints under a pixel: none of SN2, SN3 or SN10 is visible there. At eye level the design delivers 2,700 chamfered boxes wearing one grain map tiled at a metre, and the eye reads a tiled box wall. The craft study names the studios' surface model (In short 6: a light block plus shared sculpted faces in a texture array), yet SN6 demotes it to "only if R4's restraint check fails". Research and design disagree on the one thing that decides the eye-level look. The ladder sees it at R4, after R2's whole day, as last time.

**2. The faults were the pipeline's, and the new mesh inherited them.** By the study's own account, one-pixel lines, rims, specks and black slots are specular aliasing, shadow normal bias, bloom without a Karis average, and SSAO in narrow joints. The design treats them as the stone's and pushes the rest to 1c "if R4 shows it". `Stone.shader` adds marks of its own: rust spots (noise at 9× and 47× a metre), sand at 260×, film, crazing, crumb at 90×, four hue bins. None is in SN7's list; all are specks at the street stop. The cheapest test is never run: the shader fixes on today's mesh. If lines and specks fall by 90% there, the redraw owns far less; if not, it cannot fix them either. Not caught until R4.

**3. The raised views still shimmer, because L0 is the only level.** SN4's chamfers are 8 to 12 mm: 2.75 px at 5 m, 1.1 px at 12 m. The study says chamfer strips leave the mesh past 10 m; the design has no L1 "until port step 5", so into12 and high draw every chamfer of 2,700 stones at a pixel, and the shadow pass draws them again from the full mesh (the proxy is a fallback here; the study makes it the rule). The fills are long thin strips, what the M4 pays for (In short 7), and SN8 counts them nowhere. R3 measures it after the build; R2 counts triangles, not their shape.

**4. The restraint test passes by construction, and Øystein says "a bit much" again.** Done 5 wants busyness within 25% of the target at street and at most 1.5× the clay beside it, "thresholds checked on the grey-form sheet". The target's stone is three or four values with no texture; any textured wall beside untextured clay exceeds 1.5× at eye level. So the thresholds are unreachable or loosened to whatever grey form gives. Øystein judged the last build at eye level beside clay; the ladder changes neither. And there is no eye-level target: the target is one street view, so Done 8's "beside the target frame" at eye-foot and eye-on is against nothing. Caught only at R6.

**5. The design contradicts itself at the stair side, and the slivers come back there.** SN2 says every bed is level and, across the wall, each stone is "square to the battered face: a turn". A stone turned 9.5° has a bed tilted 1 in 6; stacked, the courses are not level and meet the level step ends in wedges. The study's rule is simpler: level beds, the face plane cut at the batter. The stair-side footing is a staircase of 150 mm ledges, and nothing says what the first course above each ledge does. R1 catches it only if the step ends are drawn as occupied cells, which R1 does not say.

**6. The box breaks, and the hygiene list is what gets done.** R1 is an occupancy layout with candidate scoring, bond tests and a sheet: 0.3 day. R2 is two new parts, the laying through the stages, a rewrite of `wall.py`'s courses, copings and heads (723 lines), eight new geometric checks and a sheet: 1.0 day. R4 is spec filtering, perhaps a remade grain map, three lights and three image checks that do not exist: 0.6 day. "Also in 2b" adds six chores. Honest: 4 to 5 Opus-days. The 1.5× stop fires at 3.75 with R4 half done.

## What a lead technical artist would say we are missing

- **Look-dev before kit.** One wall stone, one step, one coping, with the final surface model and shader, in the target light, at 1, 5 and 12 m. Fix: a rung R2a, half a day, before any laying.
- **A decided surface model.** A texture array of sculpted face patches by seed (four to start), relief in the patch, chamfers in the mesh to 10 m. Fix: SN6 states it as the way.
- **An inventory of marks, cut by subtraction.** List every mark the bake and shader make (grain, relief, rust, hue bins, per-piece value, polish, moss, lichen, wet, drips, streaks, sand, film, crazing, crumb). Keep three: grain, wear, moss in the joints. Fix: the list in SN7, with what was cut.
- **Pipeline bugs tested on the old mesh first.** Fix: R0b, a shading-only A/B on today's gully (GeometricNormalFiltering, the joint value floor, Karis bloom, bias 0.5 against 0.2). Half a day; it sizes the redraw.
- **An eye-level target.** Fix: paint it over R3's grey render before R4, as the rules require, the clay beside it painted as it will be, so the stone is judged in its future company.
- **Levels and a shadow proxy from the start.** Fix: L1 at 10 m (chamfers and fills gone, courses by texture) and a `ShadowsOnly` proxy in SN8, with a long-thin-triangle gate (aspect over 10:1).
- **Calibrated thresholds.** Fix: measure today's gully, the clay and the target on R0's sheet; set Done 5's numbers from those.
- **A vertex format decided once.** Six UV sets a vertex is wrong for a city. Fix: piece id, face and variation in one set, history in colour; in `docs/foundations.md` before R2.
- **Stability under edits.** One record event (the 1961 panel) re-lays that panel only. Fix: course layout keyed by panel.

## Changes to the design

1. SN6: shared sculpted face patches in a texture array are the surface model; the tiled grain map is retired. Blocking.
2. New rung R0b: the shader fixes A/B'd on today's mesh; its result sets what 2b owns. Blocking.
3. New rung R2a: three stones at full material in the target light, at 1, 5 and 12 m, before laying. Blocking.
4. SN7: a named inventory of marks, three kept, the rest cut and listed. Blocking.
5. An eye-level target painted over R3's grey render, the clay painted as planned; Done 8 judges against it. Learned at R3, before R4.
6. SN2: strike "square to the battered face"; level beds, the face plane cut at the batter. Blocking.
7. SN2 and R1: the step ends drawn as occupied cells on the elevation, with a rule for the first course above each ledge. Learned at R1.
8. SN8: L1 at 10 m and a `ShadowsOnly` proxy are the plan; fills counted; a long-thin-triangle gate. Blocking for the format; measured at R3.
9. Done 5: thresholds calibrated on R0's sheet from today's gully, the clay and the target. Learned at R0.
10. A vertex format decided in foundations before R2. Blocking.
11. "Also in 2b" moves to its own step, except `write_export`. Blocking: it is scope.
12. The box: 4 Opus-days, R2 split into R2a and R2b, the stop at 1.5×.

## Keep

- SN1, rigid blocks cut by planes, moved and turned only: the right rule and check.
- SN2's level beds, only footings and copings following the slope; kneelers at upward breaks.
- SN3's steps: two stones at most, lapped, built into the wall.
- SN4's few large planar marks, no per-vertex noise, the 2 px chamfer floor.
- SN5's filled joints no deeper than wide, with a value floor.
- SN9 and SN10 as machine checks.
- Q14's reason to start again: it was right.
- R1 on paper in integer millimetres before any mesh: the cheapest rung and the best.

## Box

2.5 Opus-days is not honest; it was written before the checks and tools in it were counted. Four days with R2 split is. Cut first: the six "Also in 2b" chores (scope, not the redraw); then lichen, per-piece hue, rust, sand, film and crazing (marks nobody asked for); then the 1961 panel's and the 1952 run's own materials (facts kept, drawn next step); then the line of minimum trace. Do not cut R0b, R2a or the eye-level target: they are the difference between this round and the last eight.
