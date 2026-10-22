# Gully on the hash spec, A against B: strict review

Coordinates are (x, y) in the 1280 by 720 crops. A nose-pitch count along the stair axis (04, 05, 08) gives the same tread pitch in both builds, about 27 px at the high camera: they differ in set-out, not in going.

## Per pair

**01, low sun, foot.** Worn noses, moss at the back of the treads, a shadowed step in the left coping, and black slits at the riser joints, in both. Equal.

**02, low sun, on the steps.** A's wall reads as heavy slabs over black voids; B's as thinner plates, some proud, with lit ends. A has a wall stone whose end is five bright vertical bars (1195-1235, 20-55), a comb that will shimmer. A worse.

**03, low sun, street stop.** Same silhouette, same open wall ends at the foot in both. In the sunlit top A shows a paved landing (760-820, 93-140); B shows treads running on. B worse.

**04, low sun, 12 m.** A has two landings in frame (300-640, 410-570 and 480-760, 95-160), paved in long slabs with fill pieces at the row ends. B has none: one continuous run at the same pitch, and deeper black slots in the left wall (273-300, 390-470). B worse.

**05, low sun, high camera.** Most of the stair is in frame. A: landings at (700-900, 430-560) and (820-1000, 190-260). B: none. B worse.

**06, drizzle, on the steps.** Same lichen, moss and slits. A has a loose block projecting from a riser below nose level (765-830, 415-450), beside a black slit; it reads as a displaced fragment with no cause. B's exposed slab end at (575-625, 280-350) is a plausible set-back. A worse.

**07, drizzle, foot.** The wall-top steps read as mossy faces here in both (A 150-200, 130-180; B 95-150, 165-245), so they are faces, not holes. Equal.

**08, blue hour, 12 m.** A: landing at (560-900, 420-600). B: continuous treads and the black wall slots at (553-575, 387-465). B worse.

## Faults

1. **No landings** (B only). B is a single run of about forty risers at the same pitch as A; the facts say two flights with landings. 03 (760-820, 93-140), 04, 05, 08 as above. If landing placement is drawn from the seed, that is a generator fault: a fact must not depend on the seed.
2. **Loose block in a riser** (A only). 06-A (765-830, 415-450).
3. **Comb of bright bars on a wall stone end** (A only). 02-A (1195-1235, 20-55). One-to-three-pixel bright bars; shimmer.
4. **Riser joints as black slits** (both). 6-10 px black rectangles at every slab-to-slab joint: 01-A (565-575, 325-365), 01-B (565-572, 370-420), 06-A (1020-1030, 80-150), 06-B (1070-1080, 240-340), 07-A (660, 100-150), 07-B (823-833, 100-130). They read as holes, not soil or cement.
5. **Open cheek-wall ends** (both). At the foot each wall ends in two splayed skins with ground visible between: 03 left (615-665, 570-690), right (1095-1140, 560-690). No mason leaves that.
6. **Wall-top step faces go pure black** at low sun and blue hour (both; B's deeper and more numerous): 01-A (70-110, 130-180), 01-B (55-100, 160-230), 04-A (250-275, 415-460), 04-B (273-300, 390-470), 05-A (610-637, 480-510), 05-B (620-650, 480-530), 08-A (525-560, 400-505), 08-B (553-575, 387-465). No ambient reaches them.
7. **One-to-two-pixel lines** at slab edges and landing joints (both): 06-A (525, 150-200), 06-B (345, 355-390; 357, 500-620), 05-A (900-947, 213-240). Shimmer candidates.
8. **Lichen on trodden tread centres** (both): 06-A (200-520, 100-300), 06-B (450-700, 60-160). Feet would have worn it from the middle of a tread; the round dots read as spots.

## Verdict

Neither build is clean. Faults 4 to 8 are in both; they set the work still to do but do not separate the builds.

**A is fit to be the reference.** Its set-out matches the facts; its two one-build defects (the loose block in 06, the comb in 02) are local. Log them, so a later change that removes them reads as a fix, not drift.

**B is not fit.** It has no landings, which contradicts a stated fact of the stair: the only defect of set-out rather than of a mark. Its deeper black wall-top slots are a lesser second difference.

## The key (unblinded after the verdict)

The two builds are the 22 October baseline (the old seeds) and the build from the generators on the hash spec (`dbd455c`). They were not labelled the same way in every pair. The hash-spec build is A in 01, 06 and 07, and B in 02, 03, 04, 05 and 08. So the reviewer's closing "A fit, B not" reads, pair by pair, as follows:

| Pair | Verdict | Which build is worse |
| --- | --- | --- |
| 01, 07 | Equal | Neither |
| 02 | A worse | The old build (the comb of bright bars on a wall stone's end) |
| 03, 04, 05, 08 | B worse | The hash-spec build (no landings on the lower flight; deeper black slots on the wall top) |
| 06 | A worse | The hash-spec build (a loose block proud of a riser) |

The crops are 1280 by 720 at native size from the 2560 by 1440 golden frames, each placed where the two builds differ most:

| Pair | Light | View | Crop corner (x, y) |
| --- | --- | --- | --- |
| 01 | low sun | eye-foot | 600, 720 |
| 02 | low sun | eye-on | 1280, 560 |
| 03 | low sun | street | 480, 640 |
| 04 | low sun | into12 | 720, 440 |
| 05 | low sun | high | 120, 640 |
| 06 | drizzle | eye-on | 0, 560 |
| 07 | drizzle | eye-foot | 520, 720 |
| 08 | blue hour | into12 | 440, 440 |

The A or B order was drawn from `h("rebaseline-seeds", n)`. The reviewer was a fresh Fable 5.1 agent, given only the crops and the bar, on 22 October.

**What the verdict rests on.** "No landings" is a fault in the set-out function, not in the seeding. The landings are not engine facts (the brief's word "facts" overstated it). They are the output of `step_plan`, which promises a landing "wherever a run of steps grows longer than its builder would climb without a rest" (the town allows 11 to 16 steps).

The lower flight rises 5.0 m over 10.2 m. When the rise drawn from the stone falls below about 0.162 m, the steps alone fill the run, and the function drops its landings without a word. That happened on the new draw: 33 steps at 0.152 m and no rest, where the old draw gave 29 steps at 0.172 m with a landing.

Swept over 500 seeds, the lower flight runs more than 16 steps without a landing in 225 of them (45 %). The upper flight (8.0 m over 33.4 m) never does. The old seed fell among the good draws, so the old build did not show the fault.

The fix belongs to the function, which needs a judged decision. On a steep run, a mason would choose a thicker block, or a shorter going within the stride rule, so that the rests fit. Choosing a seed that happens to look right would hide the fault.
