# L5: who owns the materials' shaders

1c's L5 (`reviews/lt1/playable/outline.md`), 22 October. Measured only.

## In short

- **The owner is the light the two shaders share.** Two terms every street and stone pixel pays, the town's sky (`OS_TownSky`, 2.4 to 3.0 ms) and the clouds' shadow (`OS_CloudLight`, 2.1 to 2.5 ms), cost 4.5 to 5.4 ms together in every view and light, 46 per cent of the lump at the foot and 77 at the Anchor's door.
- **Next is the stone's growth layer:** 4.6 to 4.7 ms at the foot of the steps (1.0 to 1.2 of it the young rosettes), 1.0 to 1.6 in the street and window views, none at the door. By shader, the stone owns 6.7 to 6.9 ms of the foot, the street shader 4.9 to 5.4 ms at the window and door.
- **Third is the shadow map's sample** in the two shaders, 0.2 to 2.1 ms (0.2 to 0.4 at the blue hour), measured in the noisier full frame.
- Every other term is under 0.6 ms. The terms account for 90 to 105 per cent of the lump, which the light does not change (within 0.2 ms).

## The split

Offscreen ms at 2560 by 1440, the median of two runs, the range over drizzle, low sun and blue hour (every cell: `reviews/perf/2026-10-22/l5/split.md`).

| | eye-foot | street | a-window | anchor-door |
| --- | --- | --- | --- | --- |
| bare less flat (the lump) | 11.3–11.5 | 7.2–7.3 | 7.4–7.5 | 5.9–6.0 |
| family *stone* | 6.7–6.9 | 2.8–2.9 | 1.9–2.0 | 0.0 |
| family *street* | 3.0–3.1 | 4.2–4.3 | 5.2–5.4 | 4.9–5.1 |
| town's sky | 2.8 | 2.5–2.6 | 2.8–3.0 | 2.4–2.5 |
| clouds' shadow | 2.4–2.5 | 2.1–2.2 | 2.3–2.4 | 2.1 |
| growth (stone) | 4.6–4.7 | 1.5–1.6 | 1.0–1.1 | 0.0 |
| of it, rosettes | 1.0–1.2 | 0.4–0.5 | 0.3 | 0.0 |
| shadow sample | 0.4–1.4 | 0.4–2.1 | 0.2–1.4 | 0.2–1.5 |
| air, brush, reflections | −0.1–0.6 each | 0.2–0.4 | 0.3–0.5 | 0.3–0.5 |
| lamps, near marks | ≤0.3 | ≤0.1 | ≤0.1 | ≤0.1 |

## Method

W7's lump is *bare* (every pass off: no shadow map, SSAO, SSR, MSAA or post) less *flat* (the same draws unlit). New arms in `PerfRunner`, off in the game:
- *flat-street*, *flat-stone*, *flat-water*: bare with only that family unlit; its cost is bare less the arm. Families: street (17 renderers, 1.88 M triangles), stone (the gully: 4, 0.96 M), water (2, costing nothing).
- *bare-&lt;term&gt;*: bare with one term skipped (`OS_L5_<TERM>`). A skipped term returns what it gives when absent (open sky, no cloud, no growth), never a cheaper stand-in. *bare-haze* reuses `OS_HAZE_OFF`.
- *all-shadow*: every pass on, the shadow map drawn but not sampled by the two shaders.

`Editor/Measuring/L5Strip.cs` compiles the term variants only into builds that name them; no game build carries them. `tools/shader_split.py` writes the split.

Two runs (23:06 and 23:22) with w7's settings (`-perf-frames 60 -perf-warmup 20 -perf-rounds 2`; `runs.md`, `run-*/machine.json`). The walk app was not running (checked every 10 s). The runs agree within 0.8 ms on the lump, 0.4 on every term and 1.8 on the shadow sample. Run 1 ran beside a Python batch (load 9.8 against 3.6).

## What it does not show

- Each term was skipped alone; the sky and clouds' 4.5 to 5.4 ms assumes their savings add.
- A skipped term also drops work only it needed, as a fix would.
- Terms were measured in bare, without MSAA's edge samples; only the shadow sample was measured in the full frame.
- The families fall short of the lump by up to 1.7 ms at the foot: paid only when both shaders run.
- Look P, four views, the walk's corner; no tree.
- **Golden** (`tools/golden.sh`, end against start): drizzle and blue hour identical with the arms in; low sun changed on every sunlit face (20,000 to 650,000 pixels, worst 0.08). Not L5's: with its arms out the same frames change by the same counts. It appeared after 22:47; the only other shader change since is R0b's (cd79b22). Later runs add 8 to 97 pixels in drizzle and blue hour, arms in or out. *Resolved (coordinating session, 22 October, a clean tree after a5efca7):* low sun's change is W5's beams, matching `reviews/lt1/playable/walk/w5/golden-report.md` to the pixel in all five frames. It is not R0b's. It waits for Øystein's re-bless of the low-sun frames (`NOW.md`). Drizzle and blue hour are identical to the baseline, so the 8 to 97 pixels came from the working tree at the time (M_Sky.mat and the settings files were dirty).

## Who fixes what

| Cost | ms | Owner | Fix | Saves about |
| --- | --- | --- | --- | --- |
| Town's sky | 2.4–3.0 | 1c L8, which rewrites `OS_TownSky` | per vertex or per chunk, until history changes (`docs/research/performance-craft.md`, item 2) | 2 to 2.5 ms |
| Clouds' shadow | 2.1–2.5 | 1c, with the beams | one read of the beams' cloud map (`SunBeamsQuarter.shader`) for seven noises, twice a pixel | 2 ms (research: 0.5 to 1.5) |
| Growth | 4.6–4.7 at the foot, 1.0–1.6 elsewhere | 2b's redraw of the stone (R0b, cd79b22, gives it growth's lines and specks); else the port's step 4 | the rosettes' loop only where they can be seen; the fields skipped where the facts give none | 1 to 3 ms at the foot |
| Shadow sample | 0.2–2.1 | 1c, with the sun's shadow map | a cheaper filter, judged on the frames | 0.5 to 1.5 ms |
| Air, brush, reflections, lamps, near marks | 0.4–1.8 together | the port's step 4 | none of its own | |

Together about 5 to 7.5 ms of the foot's 11.4 and 4 to 5 ms of 6 to 7.5 elsewhere, and the shadow sample's 0.5 to 1.5 besides.
