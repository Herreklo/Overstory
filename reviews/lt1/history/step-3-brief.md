# Step 3: history as a function (build brief)

For a fresh Opus builder. Current on 22 October, after R2c, step 2a (`6cf137a`) and Fable's verdict (`step-3-verdict.md`, beside this file). Start no agents unless the coordinator says so. Report to the coordinator in under 500 words; anything longer goes in a file beside this one.

**Goal.** History becomes a function of the record and the date (D5.1). The drives sit in page-group pages, the clocks in the piece table, speed and care per thing, and the date is a shader global; the stone reads `OS_History`. It must match today at 1989 (D5.2), move correctly with the date, and stay inside history's line (S2: 0.5 ms a screen at overdraw 1).

## Where it stands

| Rung | What | Commits | Outcome |
| --- | --- | --- | --- |
| R0 | craft study | `eff830d` | `docs/research/history-pages.md`: global page arrays and piece table; RGBA8, then BC7; one drive per layer, resets per piece; charts per run |
| R1 | the fit, on a frozen copy | `5bab990` | `fit.md`: amplitude × curve for polish and moss, a rate for lichen; exact in float at 1989, at most 0.5/255 in 8 bits; no texel needs an offset; the old fields move with settling; the prefix needs whole decades (2b) |
| R2 | the date, the include, the arms, the quad | `db34f2a`, `b9ccfca` | `r2.md`: `_OS_Date`, `Shaders/History.hlsl` (the law a stub), `OS_HISTORY_OFF`, `OS_HAZE_OFF`; goldens bit-identical with both arms off; +366 programs; a 16-byte GPU piece entry |
| Gate | Fable's pre-mortem and decisions 1 to 9 | | `step-3-verdict.md` |
| R1b | care as a uniform | `b67647c` | `fit.md`, R1b: moss = clip(damp·f(care), 0, 1)·T is exact; H1.B holds damp over 2.04, P0.R feet; 1.29/255 at 1989 in 8 bits |
| R2b | a sample, minified | `01d717d` | `r2.md`, R2b: 0.59 to 0.78 ms a sample on the quad |
| R2c | why minified costs | `5426153` | `r2.md`, R2c: a sample costs about 0.02 ms; a busy output costs up to 2.2 ms in the passes after the draw; the include's default path stays; S3 stands |
| Docs | the decisions in the docs and schemas | the commit that adds this file | below |
| 2a | the stair as a kind | `6cf137a` | FBX hash unchanged |

Waiting on step 2b, one re-baseline for Friday's strict review and Øystein's acceptance, judged against the target frame: H1's fields baked on each piece as laid (decision 5), the integer plan, the world seed, upkeep's whole decades, minted ids, wall-head slots.

## What is settled

Don't reopen these without new evidence:
- `docs/building-blocks.md`, "History is a function of the record and the date": the law, clocks per piece, care as a uniform, baked as laid, charts, formats, what a family reads, one baker;
- `docs/research/building-blocks-decisions.md` D5.1 and D5.4 (amended), D5.10 (new), S2 (amended);
- `schemas/layers.json` (each layer's `law`, moss's `careFactor` and `order`, the derived hollow, `readers`), `maps.json` (p0's and h1's `stores`, `charts`, `pageFormat`, `bakers`, `unknowns`), `interval.schema.json` (`reach`), `chunk-format.md` (section 4, the clocks, the GPU entry), `channels.json` (uv4.y reserved; stone writes no uv5);
- the verdict, as the coordinator corrected it: decision 4 as R1b measured (store damp, not damp × T, and clip before the thinning); decision 5 built at 2b, not 2a; decision 7 settled by R2c (the 0.25 ms bound withdrawn, 0.17 ms a sample budgeted, about 0.02 measured).

## Read first

- `CLAUDE.md`, this brief, the verdict, and the files above.
- `reviews/lt1/history/fit.md` (a), (e) and R1b; `r2.md` whole.
- `docs/research/history-pages.md` §3 and §4; `docs/measuring.md` (hashes, golden threshold, the harness).
- `schemas/stages.md`, `hashing.md`; `kinds/stair.json`, `blender/generators/stair_stages.py` (life, bake), `fixtures/golden/stair/`.
- Code: `wear.py`, `growth.py`, `water.py`, `upkeep.flight`; `Stone.shader`, `Growth.hlsl`, `History.hlsl`, `StreetSurface.hlsl`; `PerfRunner.cs`, `LT1Stone.Stage`, `LT1Golden.Views`, `LT1History`.

## Rungs left, in order

R3 waits for 2b's as-laid bake, since H1 is baked as laid.

**R3. Intervals and pages.**
- Life writes intervals per fill and layer, validated against `interval.schema.json`, with `reach` for a lift by hands or a relaid bed. `upkeep.py` untouched.
- The piece table as `chunk-format.md`: 32 bytes on disk; four resets (placed, disturbed, cleaned, reserved) as year × 16 + month from the pack's first year, months 1 to 12, 0 for none; the age brought in whole years; inherited polish, variation, flags.
- One bake function (`blender/generators/pages.py`), which the player's bake matches at step 5 (`maps.json`, `bakers`):
  - each piece to its 4 m chunk and 16 m group (`hashes.chunk_of`), its texel from `face_class.py` through a face-kind-to-facing table in `kinds/stair.json`;
  - charts from UV0 per run of one face kind, joints inside, on a 16-texel grid with 2 texels of padding, shelf-packed into 1024×512 pages; barycentric fill, dilation, three mips baked within each chart;
  - linear RGBA8 P0, P1 and H1, one array slice per group and page. H1 as `maps.json`'s `stores`, baked on each piece as laid; P0 at the settled position, its R feet (mtr / trod).
- Vertex: UV1 the address; UV3 piece index and edge distance; UV4 face kind, 0 (the hollow rate, reserved), 0, own occlusion; UV5 dropped. `bakeVersion` covers the include and the shader.
- Accept:
  - two builds hash the same, and golden page hashes are written;
  - `mesh_hash.py compare` against 2b's build: positions, normals, faces and UV0 unchanged;
  - no vertex addresses outside its chart; packing waste reported against 150 ‰, pages against 4 MB a flight; the bake at most 60 s;
  - the real pages' BC7 error (bc7e through `EditorUtility.CompressTexture`), per page, channel and mip 0 to 2: 99th percentile at most 2/255, H1.B about 1/255 stored. This picks each page's format before R4; a failing pair is named for BC5;
  - a page debug view (each channel, chart borders) and a date scrub, in the editor;
  - goldens rewritten in their own commit.

**R4. The stone on pages.**
- `Stone.shader` reads `OS_History`, the piece table and `_OS_Date` in place of UV1 to UV5's history (`fit.md` (a)). It samples P0 and H1 only (D5.10).
- The law goes into `OS_HistoryLaw` as `layers.json` has it: moss clips before the thinning; the hollow's held water and the tread's water are derived.
- Care, trod, footfall and the wear rate are per thing: globals for now, care the thing's of year t − 1.
- The GPU entry as `chunk-format.md`: u16 slice and variation, the four resets, the age, inherited polish, flags.
- `Growth.hlsl` and `Water.hlsl` keep their signatures.
- Accept: the player compiles; `_History` at 1989 matches `fit.md` within 2/255 at 20 sampled vertices.

**R5. The A/B (D5.2).**
- `LT1Golden.Views` gains `-grey`. A is 2b's as-laid build with today's shader, rendered in the same session as B.
- Every frame is shown beside the target frame (`reviews/lt1/heart/target/3-street-gully-steps-target.png`), and the verdict names where the gully stands against it: Øystein is not sure the before version is the right comparison.
- Accept: all 15 frames in colour, plus eye-foot and eye-on in grey, each with a mean at most 0.0005 and a worst pixel at most 0.05; RGBA8 first, then R3's formats.
- Grey alone is blind: `_Grey` replaces the albedo and hides the layers' pigment.
- On failure, change one thing at a time (float pages, then 1 cm texels, then the law); then the coordinator runs a blind review of the worst crops. If the fronts' feet read dead, their band moves to P0.G (verdict 5).

**R6. The years sheet.**
- Numbers first:
  - at the care changes (1930, 1946, 1965), the moss jump equals the old code's within 1/255 on the fields the two builds share (R1b: 0.62 to 0.77). Where the year's settling moved the fields, the difference is decision 5's as-laid change: report it, don't fail it;
  - at 1911 and 1952, change only in the pieces life names, 0 texels elsewhere;
  - layers monotone between events.
- Frames at eye-on and the street stop, in drizzle, colour and grey: 1951, 1953, 1964, 1966 and 1989 each built at its date; 2005 is the 1989 build with the date alone. This checks the function; it is not a past shown to players.
- Watched against jumped: the 1966 build against the 1989 build at date 1966, FLIP reported; the hollow is the expected difference.
- A motion sheet across chart borders at mips 1 and 2 (`maps.json`, chart-shimmer).

**R7. The four arms on the gully.** Eye-on and the street stop, drizzle, two rounds. Accept: all minus history-off, projected per stone pixel to the street stop, at most 0.5 ms. The quad's numbers do not transfer: history costs what it changes in the stone's already textured output, paid in the passes after the draw (R2c). Give the presented frame's GPU time beside the offscreen time.

## The cut line

R1b, R2b, R2c and the decisions in the docs and schemas are done. If 2b's as-laid bake lands in time: R3, R4 and R5 at eye-foot and eye-on in RGBA8, shown as they stand at Friday's review. R6, R7 and the BC7 frames go to next week. Never leave a half-ported `Stone.shader` on the branch: R4 commits only with R5's frames.

## Unity rules

- `pgrep -fl Unity` before any batch run; never run while another Unity has `unity/` open.
- Waiting for a run: `pgrep -f <pattern>` matches the waiting shell's own command line, so a loop on it never ends. Wait on the real pid, or use a pattern that cannot match itself (`pgrep -f '[U]nity -batchmode'`).
- Never edit, save or commit `unity/Assets/Experiments/LT1/Heart/LT1_Heart.unity`. `LT1Stone.Stage` opens it without saving: hash it before and after each run.
- No stage is ported to C# this week: only the shader side, the date global, page binding, and the harness and golden arms.
- A stripping rule comes before any new `multi_compile` arm.
- The harness player takes the screen for 11 to 42 minutes: ask the coordinator before each run.

## Shared constraints

- The checkout is shared with other sessions on `lt/1-harbour-street`. Commit only your own paths (`git commit <paths>`), push each commit, and never switch branch, stash or reset. Never edit a file with uncommitted changes you didn't make. `NOW.md` is the main session's.
- Messages are `LT1: <what changed>`, ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Two Pythons, neither to be changed: `.venv/bin/python` (3.9.6, jsonschema 4.25.1, no numpy) for the validators; Blender 5.2.2's (3.13, numpy, no jsonschema) for the stages, `/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python <script> -- <args>`.
- Before each commit: `tools/naming.py --check`, `tools/validate_record.py --self-test`, `tools/migrate.py --check`. A contract change takes a `schemas/CHANGELOG.md` line.

## Files it will create or change

- **New:** `blender/generators/pages.py`; the page debug view and date scrub; the pages with a hash manifest; golden page hashes; R3 to R7's notes in `reviews/lt1/history/`.
- **Changed:** `stair_stages.py`, `kinds/stair.json`, `tools/hashes.py`; `Stone.shader`, `History.hlsl`; `LT1Golden.cs`, `LT1Stone.cs`, and `PerfRunner.cs` or `LT1Perf.cs` if R7 needs it; goldens `fixtures/golden/stair/life.json`, `bake.json`; `docs/measuring.md`, `building-blocks.md`, `systems.md` with the outcomes.

## What would change our minds

- No 4-channel H1 fits within 2/255 on real pages: a layer needs two quantities per texel, which takes an H2 channel, not a second law. To Fable with the numbers.
- BC7 fails on every channel of a real page: H1 becomes two BC5 pages, one more sample against D5.10.
- History on the real stone costs over 0.5 ms a screen at R7: to Fable. The output's busyness is the first suspect, not the sampling.
- The A/B passes only at 1 cm, or only with risers at 2 cm: evidence against S3's texels.
- The moss jump at a care change misses the old code's by over 1/255 on shared fields, or anything moves outside life's events: the interval model or life's prefix is wrong.
- A kind needs a fifth clock: D5.4 reopens.

## Known unknowns (rung where learned)

1. **The real pages' BC7 error**, per channel and mip (R3's end, before R4).
2. **Charts:** packing waste per run, and whether UV0 islands overlap within a piece (R3).
3. **History's cost on the real stone's busy output** (R7).
4. **Chart shimmer** at borders, mips 1 and 2 (R6).
5. **Risers:** face class gives them 40 mm, and their feet carry a 4 cm damp strip (R5).
6. **Reclaimed stone:** the gully has none at any build, so the inherited polish and the age brought are untested (`fit.md`); test them on the first record that has one.
7. **The page binding's Resident Drawer variant** (3.4, with the Drawer's pragmas).
8. **The player's GPU encoder** (step 5; step 3 bakes offline).
9. **The hollow** is still geometry, so a jump is not yet a uniform for wear (past the cut); its water is already derived.
