Not for Øystein: test 4 stays blind.

# Test 2a: is the clue in line of sight?

**Fail on the pass line; a change, not a kill.** The pass line (outline §3, test 2) asks that one vantage see both doors and most of the climb. No vantage does. A's back first-floor window sees 83% of Hannah's climb and E's door, but not Hannah's door, and no vantage tried sees both. The climb and its end are in the pixels from the player's own house. The miss is one authored value, Hannah's home at Low Terrace up 18, whose door Low Terrace down 9 and the windows' reveals hide from A, the Row and the Anchor. Moving that home re-casts the frozen case, so it is the case's next decision, not mine.

`tools/playable/sight.py` reads the frozen case (sha256 `876b3185…`) and the heart's layout as `layout_dump.py` dumped it (`2a-layout.json`). Its toy rays, window, camera and clock ran first (`tools/tests/test_sight.py`, 7 of 7). Full output: `2a-sight-run.txt`.

**Added since the pick:** the birch at (44.5, 28.0), its crown run bare and opaque (**the crown changes nothing**: A's lines pass under it; the trunk matters only from the ground floor); the stone walls, yard walls, sheds and stoops (they block most of the climb from the ground floor); and A's 20 real windows and shopfront from the 1989 plan, glass set into the wall, the eye behind it free to lean 0.3 m.

## Hannah's climb, her door to E's (the birch either way)

| Vantage | Head in sight | Whole figure | Longest run | Her door | E's door | Px, Lens35 (far, median, near) |
| --- | --- | --- | --- | --- | --- | --- |
| A, back first floor, x 45.6 | 83% | 66% | 31 m | no | yes | 50, 93, 248 |
| A, back first floor, x 41.1 | 82% | 65% | 34 m | no | yes | 46, 76, 220 |
| A, back first floor, x 43.3 | 75% | 58% | 26 m | no | yes | 50, 88, 235 |
| A, back ground floor (best) | 31% | 28% | 22 m | no | no | 121, 187, 239 |
| A, front and side windows (their reveals) | 0% | | | no | no | |
| The Row (49.3, −12) | 77% | 59% | 55 m | no | no | 38, 58, 103 |
| The Anchor's door, Row 22 or 24 | 0% | 0% | | no | no | |
| *Elsewhere:* the steps' foot | 80% | 58% | 57 m | no | no | 45, 78, 172 |
| *Elsewhere:* the Low Terrace at the steps | 41% | 34% | 29 m | **yes** | no | 192, 480, 4082 |
| *Elsewhere:* the Landing (45, 42) | 85% | 63% | 56 m | no | yes | 76, 189, 1551 |

From x 45.6 the climb spans 42°, inside Lens35's 62.5°, so one frame holds it. The Row sees the climb only at the steps' mouth: swept along y −8, x 50 gives 77% and every other point 6% or less. **Doors seen from A's back first-floor windows:** E; D (empty since 1986, so nobody's); High Terrace up 20 (x 38.8 to 43.3, 34 m off); Top Terrace up 21 (x 38.8 and 41.1, 70 m). Hannah's door, 22 m off, is lost to the reveal and Low Terrace down 9; Karen's (High Terrace up 21) and C's are behind C.

## The other routes (head in sight; the whole figure is close behind)

| Route | A, x 45.6 | The Row | The Anchor's door |
| --- | --- | --- | --- |
| Olive, Anchor along the Row and up to E, from Row 22 (the frozen case) | 50% | 94% | 36% |
| Olive, the same, from Row 24 (where W3 cast the Anchor) | 58% | 93% | 25% |
| Seed B: Ben, Row 23 to Andy's door | 24% | 87% | 52% |
| Seed B: Oliver, B to Andy's door | 37% | 79% | 26% |
| Seed B: Trevor, along the Low Terrace | 53% | 19% | 0% |

No vantage sees Andy's door (Low Terrace down 9) except the Low Terrace at the steps.

## The sun at the authored hours (Stavanger, the clocks of the year)

November's Wednesdays: 15:30 at +3.7, +2.3 and +1.2°, 16:30 at −2.3, −3.6 and −4.6°; sunsets 16:17, 16:04, 15:53. Friday 15 December 1989: sunset 15:40, 16:00 −2.6°, 18:00 −15.8°. Seed B is in daylight (September +21 to +32°; Friday 16 October 1998, summer time to the 25th, 18:00 at +2.9°, sunset 18:31). Hannah's 16:30 climbs are in civil twilight, so blue hour is the real light, not a stand-in. Olive's 15:30 is the last low sun, which hills beyond the layout may hide.

## What it means

- **The clue is in the pixels from A,** but as "someone climbs to E", not "Hannah leaves her door". Reader A in 2b could name E's door. For the start, they would have to infer it from where the figure first appears.
- **The case spec's sightings undercount the Row.** At the steps' mouth the Row sees 77% of Hannah's climb, not only Olive, though small: a median of 58 px at Lens35.
- **The change, for the case's next decision** (not done here):
  1. Move Hannah's authored home to a door seen from A's back windows. High Terrace up 20 is the nearer candidate. Homes are authored (#59), so no engine fact moves, but the frozen block's hash changes and test 1 reruns.
  2. Or the player watches from different places on different Wednesdays. The Low Terrace at the steps sees her door, which is a play change.
- **The Anchor:** W3 has since cast it onto Harbour Row 24. The frozen case still says Row 22, so test 1's walks to the Anchor run about 22 m too far. The next case should take Row 24.

## This rung's limits

- **The heart's masses, not the walk's generated houses,** which are a little smaller, so blocking by the five houses is if anything overstated.
- Simple roofs; no lamps, rails, washing or people; A blocks its own view only at each window's opening; the crown an assumed 3.5 m ellipsoid; the ground the layout's 1.5 m grid, ending at its edge.
- **It says nothing of light, contrast, drizzle or whether a reader can tell one figure from another.** That is 2b's work, and 2b checks this rung against a still.

## What 2b must know

- The best eye is A's back first-floor window at x 45.6 (y 10.7), about 1.6 m above its floor. x 41.1 is close behind and sees two more doors.
- Use Lens35. The climb spans 42° and the figure is 50 to 248 px.
- November's 16:30 is real civil twilight.
- The birch's crown does not matter; Low Terrace down 9 and the reveal do. The Row sees Olive well (94%), Hannah only from x about 50; the Anchor (Row 24 in the walk's scene) sees none of her climb.
