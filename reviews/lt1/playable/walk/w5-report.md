# W5: low sun's beams at a quarter of the pixels

LT1g, the walk, 22 October. Branch `lt/1-harbour-street`.

## In short

- **Cost.** The beams alone now cost about 1 ms, down from 62.
  - B (the new pass) averages 0.9 ms over 18 view-runs. The median is 1.0, the standard error 0.3, and single readings run from −0.9 to +2.9 ms. That is inside the harness's ±2 ms noise, so the brief's 0.5 ms can be neither confirmed nor ruled out.
  - A (the old full-size pass) costs 54 to 70 ms, 62 on average.
  - Both are measured in one build, in one no-tree run (`reviews/perf/2026-10-22/playable/w5-final/`: two runs of three rounds, nine views; "beams alone" is the arm less the same view without beams).
- **Whole frame in low sun.** Offscreen time, run 1 / run 2:

  | View | B | A | No beams | Presented frame, B | Presented frame, A |
  | --- | --- | --- | --- | --- | --- |
  | Foot of the steps | 35.2 / 38.3 ms | 96.8 / 90.3 | 36.1 / 35.7 | 31.8 / 30.9 | 83.8 / 79.8 |
  | On the steps | 31.1 / 34.4 ms | 98.2 / 93.4 | 30.7 / 32.5 | 27.6 / 26.9 | 83.1 / 82.0 |

  Low sun now costs what drizzle costs (24 to 44 ms offscreen in W3's baseline).
- **Shimmer.** B is A's equal; same-day A and B, gully, low sun, `tools/motion.sh`:

  | Path | Shimmer, A → B (levels) | Flicker, A → B |
  | --- | --- | --- |
  | Still | 0.4719 → 0.4721 | 0.156% → 0.160% |
  | Still, no dither | 0.0000 → 0.0000 | |
  | Walk | 1.1858 → 1.1858 | 7.255% → 7.255% |
  | Walk, no dither | 0.8852 → 0.8847 | |

  A still camera gets no shimmer from the beams. The pass has no time term, and with dither off a still sequence is identical frame to frame.
- **What the eye sees.** The same shafts at the same strength.
  - The golden frames in low sun move by a mean of +0.001 to +0.040 levels of 255 (absolute 0.002 to 0.070), and by at most 3.7 to 4.1 levels at single pixels.
  - Side by side at native size, no difference can be found. Only a ×8 difference map shows the beams' soft shapes, about one level apart.
  - The old pass's grain is gone.
- **Golden at the end** (`tools/golden.sh`, every light).
  - Drizzle and blue hour are bit-identical, all 10 frames.
  - The five low-sun frames fail the thresholds, as they must when a pass changes: FLIP-like mean 0.0002 to 0.0065, worst pixel 0.055 to 0.079.
  - The baseline is not re-blessed. Sheet and report are in `w5/golden-*`.
- **Verdict:** keep B. The old path stays selectable (`SunBeamsFeature.fullSize`, and the harness's `beams-full` arm) at no cost a frame.
- **Open faults:**
  1. A faint seam along depth creases nearest the camera, at the frame's edge. It reaches up to 17 levels at single pixels at the foot of the steps, (0, 1248). It is invisible at 1× and shows only in a ×8 difference.
  2. The 0.5 ms target sits below what the harness can resolve. A GPU timer on the pass would settle it.

## What was built

`unity/Assets/Shaders/SunBeamsQuarter.shader` and `unity/Assets/Code/Scenes/SunBeamsFeature.cs` (a Render Graph renderer feature) replace the full-size `FullScreenPassRendererFeature` in `PC_Renderer.asset`. They sit in the same slot, under the same name, "SunBeams", so the harness's `-beams` switch and `LT1Heart.EnsurePass` still find them. The light is the same as `SunBeams.shader`'s: the same air, the same phase, the same cloud layer and the same strength. Only the cost changes.

0. **Cloud map.**
   - The cloud layer's field is drawn once into a 512² R16F map: 8 m a texel over 4,096 m, on a fixed world grid.
   - It is drawn again only when its square moves (the camera strays 1,024 m), or when the cloud size or drift changes.
   - A step reads one texel instead of seven noises. Outside the map the field is computed as before.
1. **March.**
   - The march runs at half width and half height, with 16 steps a ray and one hard shadow tap a step (the hardware's 2×2 compare, no soft-shadow filter).
   - Each step is offset by a 4×4 ordered pattern.
   - Each half-size pixel marches for one of its four full-size pixels: the nearest on one checkerboard colour, the farthest on the other.
   - A directional light's shadow coordinate, the cascade spheres' distances and the point on the cloud layer are all affine (or quadratic) in the step's distance. They are found once a ray, so a step costs no matrix and no cascade search.
   - The step weights are now unbiased (`ds = t(2i+1)/N²`). The old ones covered about 97.5% of the ray. This is the +0.03 to +0.04 levels at 12 m and on the steps.
2. **Blur, across then down.**
   - Five taps, weighted [1 2 2 2 1]/8, so each 4×4 tile of the pattern weighs all 16 offsets the same. The march then acts as 256 stratified steps, and the pattern cancels exactly where the ray's length is smooth.
   - Taps are weighed down by how much the ray's length differs, so no beam crosses an edge.
3. **Composite.**
   - At full size, added onto the frame with no copy of it.
   - It weights the four half-size neighbours by bilinear weight and by how near each one's ray length is. Where none is near (a thin pole against the sky), it takes the nearest alone.
   - The phase is evaluated per full-size pixel.
   - The pass is skipped entirely when the light has no beams (drizzle, blue hour).

**How the frame meets the beams.** The harness tried three arms (`w5-arms`, no tree): blending onto the frame (B), compositing over a copy of the frame (`beams-copy`), and no composite at all (`beams-nocomposite`). They cost the same within noise, −0.4 to 4.2 ms each, so the remaining millisecond is the march and the blur, not the composite.

## Measurements

**Frame time.**
- `reviews/perf/2026-10-22/playable/w5-final/` (no tree, which is how the walk ships): `all` (B), `beams-full` (A) and `-beams`, nine views, two runs of three rounds. The runs agree within 9.9% offscreen.
- `w5/` (19:54): the same arms with the card birch in the scene. Compare A and B only within a run. B's beams alone read 1.1 to 3.7 ms, A's 58 to 66.
- `w5-arms/` (no tree): the composite arms.

Beams alone, offscreen, run 1 / run 2 (`w5-final`):

| View | B | A |
| --- | --- | --- |
| Foot of the steps | −0.9 / 2.5 | 60.7 / 54.6 |
| On the steps (eye) | −0.7 / 0.4 | 60.5 / 59.8 |
| Street stop | 1.6 / −0.5 | 61.1 / 54.0 |
| Into the 12 | 0.9 / −0.6 | 62.2 / 55.6 |
| 12 m | 1.1 / −0.7 | 60.7 / 58.2 |
| A's window | 1.4 / 0.2 | 64.0 / 61.8 |
| On the steps | 0.4 / 1.9 | 67.5 / 61.0 |
| The Row | 2.1 / 2.9 | 68.2 / 66.6 |
| The Anchor's door | 2.9 / 1.8 | 70.0 / 68.6 |

**Motion.**
- `w5/motion/`: the shimmer sheets and tables. `shimmer-B.md` and `shimmer-B-still-nodither.md` are B's. `shimmer-A-sameday*.md` are A's, rendered with `fullSize` set for those runs only and set back after.
- A's sheet of 21 October (still 0.4694, walk 1.1701, walk with no dither 0.8633) is from before the gully's new geometry, so the same-day A is the comparison.

**Stills.**
- `w5/*-low-sun-A-full.png` and `*-B-quarter.png`: the foot of the steps, the street stop and 12 m in the walk's player at 2560 × 1440. They come from one harness build, run 1.
- `w5/crop-*.png`: A | B | ×8 difference, at native pixels doubled, on the shafts and on the edges where A and B differ most.
- `w5/golden-crop-*.png`: the same for the golden gully.

**A trap in comparing frames.** URP's post-processing dither is indexed by the frame count. Two renders whose views were drawn in a different order or number therefore differ by about ±1 level at every pixel (mean absolute 0.45), whatever the passes. My first stills (`-moments 1600` alone) and the harness's A and B screenshots differ from each other mostly by that. Only a full `tools/golden.sh` run lines up with the baseline frame for frame, and it gives the small numbers above.

**The into12 differences in drizzle and blue hour.** W7a saw them while this work was uncommitted. They are not this change's:
- Another session's golden run at 19:43 showed them too (into12: 17 pixels in drizzle, 2 at the blue hour, worst 0.03), before my pass was in the renderer.
- My golden at the start had one stray pixel at the blue hour's 12 m.
- At the end, after both runs of my own, all 10 frames in those lights are bit-identical.

They came from other sessions' uncommitted state at the time, or from noise. The settings files W7a saw changed were the harness's own transient edits, which `tools/perf.sh` restores. This change touches only `PC_Renderer.asset`.

**The gully is unchanged:** stairs `bff7858b698f3efd`, walls `0a3d7db3100df20b`, rechecked by every compose.
