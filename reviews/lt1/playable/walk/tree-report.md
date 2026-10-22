# The walk without its birch until 1e

LT1g, Phase 1a, 22 October 2026, Opus 5.5. This sits beside W3 and W4 and carries out proposal Q16 (`docs/proposals.md`). Everything is in the commit that adds this report.

## In short

- **The walk's build has no tree until 1e rebuilds the birch.** One switch in `LT1Play.Compose`, `-tree none|clay|card`, defaults to `LT1Play.TreeDefault = "none"`. The harness's playable arm (`LT1Perf.BuildPlayable`, through `ComposeOpen`) takes the same default, so **from now on the gate's baseline has no tree.**
- **A clay stand-in was tried first and failed.** It used the greybox's own clay (M_Street in clay mode), had 1,760 triangles and drew five crown masses on limbs. Øystein judged it "so incredibly big and lumpy". He was right: the crown hung at head height over the steps' mouth and was wider than the eaves, because it was sized from the card birch's bounds, which include the spread of its cards. It stays behind `-tree clay` only so it can be compared, and no more work goes into it.
- **The card birch stays behind `-tree card`** so that 1e can compare against it.
- **What it saves:** the birch's 11 to 17 ms where it is in view.
  - W3 measured it in low sun: +12.6 at the street stop, +10.7 at 12 m and +17.4 at the city camera.
  - This session repeated the A/B in drizzle, two runs each: the offscreen frame was +11.8 ms at the street stop (40.3 against 28.5) and +15.6 ms at the city camera (44.6 against 29.0).
  - The walk's frame without the tree is 23.4 ms at the street stop and 23.8 ms at the city camera, against 33.4 and 36.7 with it.
- **The checks pass.**
  - `Check()` prints `0 trees (none)` and PASS: 5 houses, the gully's hashes unchanged (stairs `bff7858b698f3efd`, walls `0a3d7db3100df20b`), 3 rigs.
  - `CheckProxies` passes. The birch never had a collider, so none had to go.
  - `tools/golden.sh`: the 10 frames in drizzle and at blue hour are identical. The 5 low-sun frames differ (mean 0.0002 to 0.0065). That comes from W5's uncommitted beams in this checkout, not from this change: golden never calls Compose. The same 5 differed before this change's first Unity run.

## The switch

| `-tree` | What is planted under "Trees (the corner's birch)" | Check expects |
| --- | --- | --- |
| `none` (default) | nothing | 0 trees, kind none |
| `card` | the card birch, `tree_birch_s1_a60.fbx` (`LT1Perf.PlantBirch`) | 1 tree from `Assets/Art/Trees/birch/` |
| `clay` | `tree_birch_s1_a60 (clay)`: a clay mesh in M_Street, built from the card birch, which is then removed | 1 tree, that name, in M_Street |

- The code is `LT1PlayTree.cs`, a partial of `LT1Play`, with the changes in `LT1Play.cs` (ComposeOpen and Check) and `LT1Perf.cs`.
- With no tree, the leaves' bounds handed to `PlayCorner` and `PerfRunner` are empty arrays.
- `PerfRunner` adds its `-nobirch` A/B segments only when there is a tree (`birches.Length > 0`), so the default harness run has none.
- `LT1Perf` refuses to build if the scene's tree does not match the switch.
- `-perf-ab <lights>` picks the lights the A/B runs in. The default is low sun, as before. The drizzle numbers above used it.

## The clay stand-in, for the record

- Its girth comes from the card birch's bark at 0 to 0.3 m and 1.1 to 1.5 m.
- Its crown masses come from the leaf pivots, split by tree.py's own method (spatial masses, k = 5 at 16.7 m). Each mass is an ellipsoid at 2σ, rounded halfway to a sphere and drawn as an icosphere with two subdivisions.
- The trunk runs to the top mass, with limbs from the fork. The whole tree has 1,760 triangles and casts shadows. It is seeded only by the birch's own mesh.
- **What it showed:** sizing a crown from a card tree's bounds brings the cards' spread along, so the volume is far larger than the leaf mass reads. 1e should take the crown's extent from the growth record's clusters, not from rendered bounds.
- **Its cost was not measured.** A short A/B in drizzle was queued behind W5's harness run, then stopped once the default became none.

## Stills

`tree/` holds the five judging views in drizzle with no tree: eye-foot, eye-on, street, into12 and high. They replace the clay stills.
- C's yard above the steps is empty, the steps' mouth is clear, and no shadow or sky-map mark is left behind. The sky map is rebuilt over the town as composed.
- The corner reads as the clay town and the stone, with nothing standing in for the birch.

## Faults and loose ends

- **W5's harness runs this evening differ in whether the tree is present.**
  - `playable/w5` (19:54) ran with the card birch.
  - `playable/w5-arms` (20:18) compiled this switch from the working tree and ran with no tree.
  - Arms inside one run compare fine, but numbers across the two do not.
- **Golden's low-sun frames:** see the golden line above. The golden scene is staged by `LT1Golden.Views` → `LT1Stone.Stage` and never calls Compose, so this change cannot reach it. In this checkout W5's uncommitted beams (`PC_Renderer.asset`, `SunBeamsFeature.cs`, `SunBeamsQuarter.shader`) change the low-sun frames while W5 works.
- **`tools/playable/sight.py` still models the birch** (a trunk cylinder and a crown ellipsoid at (44.5, 28.0)) for its sight lines. It is an analysis script and was left unchanged. When the next sight-line analysis runs, the birch should be dropped or put behind the same switch.
- **The app in `unity/Builds/Playable/` is rebuilt with no tree.** W5's work was uncommitted when it was rebuilt, so W7 rebuilds at the end as planned.
- **Perf folders:** the card A/B is in `reviews/perf/2026-10-22/tree/card/` (`runs.md`, both runs).
