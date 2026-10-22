# The gully port: handover (22 October)

The port is paused at a clean point, with everything pushed to `lt/1-harbour-street` and nothing running. It resumes next week inside the playable corner.

## Done

- **Step 1, the contracts as files:** `0018d9b`, with `f17a92c` and `93a7d71` moving the fixture writers to schemaVersion 2, and the naming grammar settled in `cafec5e`.
- **Step 2's groundwork,** the hash chain, the stage runner and `diff_stage.py`: `3cf4a46`.
- **Step 2a, the stair as a kind:** `6cf137a`.
  - What it is: `kinds/stair.json`, `fixtures/records/st-gully.json`, the stages in `blender/generators/stair_stages.py`, and golden fixtures per stage in `fixtures/golden/stair/`.
  - Hashes unchanged: stairs `bff7858b698f3efd`, cheek walls `0a3d7db3100df20b`. Øystein accepted these on 22 October as the regression reference only (`03258f1`).
  - Golden views: 16 of 16 bit-identical.
  - The installer no longer rewrites an FBX whose hash is unchanged.
- **Step 3's early rungs:**
  - R0, the craft study (`eff830d`, `docs/research/history-pages.md`);
  - R1 and R1b, the fit (`5bab990`, `b67647c`, `reviews/lt1/history/fit.md`);
  - R2, R2b and R2c, the date, the include and their cost (`db34f2a`, `b9ccfca`, `01d717d`, `5426153`, `reviews/lt1/history/r2.md`).
  - A minified page sample costs about 0.02 ms a screen. What costs is how busy the output is, so S3's texels stand.
- **Fable's pre-mortem and verdict** are in `reviews/lt1/history/step-3-verdict.md`. R1b corrected decisions 3, 4 and 8, and R2c settled 7. All of it is written into the design docs and schemas in `613e1d1` (D5.1, D5.4, D5.10, S2, and the schemas `maps`, `layers`, `interval`, `chunk-format` and `channels`). The current brief is `reviews/lt1/history/step-3-brief.md`.

## Left, in order

1. **2b, the deliberate changes, ending in one new baseline.** The baseline is proposed for the strict review and accepted by Øystein against the target frame.
   - **Rocks are rigid (BB3; Øystein, 22 October: "you can not bend rocks").** This comes first. In `wall.py`:
     - each face stone and coping is sheared along its course's rake (`zv = bm + hrel + (sv - sm) * kb`), with its ends kept plumb;
     - each hearting stone follows the eased curve vertex by vertex (`base(sv) + hrel`), so it bends near a change of pitch, and leans back by a shear;
     - in `stone.py`, the slabs' settling tilt is a small-angle shear (`z += px * tilt`), under 0.2 mm off a true rotation.
     - Every stone is to be placed by moving and turning it.
     - The courses through a change of pitch step or taper as a mason lays them (open fault 1 in `measuring.md`). Study the craft first: how masons course a wall beside steps, raked or level and stepped, and how they meet at a change of pitch.
     - Add the export's rigidity check: each rigid piece against its part mesh, by its best rigid fit, failing over 0.1 mm.
     - Soil and moss in the joints may follow the curve.
   - Planning:
     - the lane and the plan in integer mm;
     - the world seed 1989, retiring `legacySeed`;
     - upkeep drawing whole decades (2 events in 1986 move).
   - Ids and slots:
     - the eight `--` ids minted;
     - slots for the wall heads;
     - the seed keys renamed.
   - History: H1 and the fields baked on each piece as laid (verdict 5).
   - The runner should hash a record's content and stop at unchanged outputs (early cutoff), as `schemas/hashing.md` says.
   - `wall.py` adopts `write_export`.
   - 2a's leftovers are in its report (inline literals, `stairs.json` without a schema, and the others).
2. **The strict review of steps 0 to 2:** a self-check first, then Fable from a lean packet. Renders sit beside the target frame (`reviews/lt1/heart/target/3-street-gully-steps-target.png`).
3. **R3 to R7, by the brief:**
   - R3 waits for 2b's as-laid build;
   - R4 changes R2's `OSPiece` struct to the new 16-byte entry;
   - R5's A is 2b's build.

## Traps

- **Unity's batch mode locks the project.** Run `pgrep -fl Unity` right before each run. The perf player takes the screen and needs the machine to itself, so run no Blender beside it.
- **`pgrep -f` matches the waiting shell's own command line,** so a loop waiting on a pattern never ends. Wait on a pid file instead.
- **Spotlight's `mds_stores`** runs at 30 to 43% CPU. Treat it as a steady background load.
- **The golden frames in `reviews/golden/baseline` are still the 21 October set.** Compare against a render made before the change.
- **`LT1_Heart.unity` holds another session's uncommitted changes.** Never save it.
- **There are two Pythons:**
  - `.venv`: 3.9, with jsonschema and no numpy;
  - Blender's: 3.13, with numpy.

The port's full plan and its agents' reports are in `reviews/lt1/port/` (copied from the shared notes folder by the plan review on 22 October; read this copy): `gully-port-plan.md`, `step-1-report.md`, `step-2-split-plan.md`, `step-2a-report.md`.

**Before step 4 opens,** read `reviews/lt1/port/foundation-needs.md`: what steps 4 and 5 must leave room for, which stone alone would not show, and the three records each step must validate (the plan review, 22 October).
