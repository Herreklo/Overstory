# Step 2a report: the stair as a kind (Opus 5.5, 22 October)

## Result: everything passes
Commit `6cf137a`, pushed, 22 paths, all mine.

- **Stairs** `bff7858b698f3efd` (354,126 triangles), passing both times through the runner:
  - run A was cold and wrote the goldens;
  - run B rebuilt with no cache, and all seven stages and their chain matched the goldens bit for bit.
- **Old command** (`stone.py -- gully`): the same hash, and the old JSON keys are identical in text and order.
- **Walls** `0a3d7db3100df20b` (607,872 triangles), and their JSON is identical.
- **Variety**: all 12 FBX entries are the same, and no old key differs in any of the 25 JSON files.
- **Golden views**: all 16 files are bit-identical to `2a-before`. `LT1_Heart.unity` and `unity/` are unchanged, and `M_Sky.mat` is restored.
- **Contract checks**: `validate_record.py`, `migrate.py --check` and `naming.py --check` pass.
- **Tests**: `test_stages.py` passes 15 of 15 in both Pythons. Three are new stair tests:
  - the kind and the record;
  - the chain to bake against the goldens, plus the cache;
  - the id level of every plan, life, geometry and sidecar id.
- **Cache**:
  - a second run skips all seven stages;
  - `--date 1990` and a slate crack-rate change each rerun from life (facts and plan skipped);
  - a `stairs.json` change reruns from plan.
- **`diff_stage`** works on the stair and names each difference by id.

## The installer (your ruling)
- `stone.write_export` exports to a temp folder and hashes the trial file.
- It replaces the installed FBX only when its manifest entry differs.
- It writes the sidecar and the manifest only when their text differs.
- In run B all three kept their mtime and size, and the installed FBX is git's bytes.
- `wall.py` still writes straight to its path, and it doesn't create its folder. It could call `write_export`.

## Where `stone.py` went
- **Kept in `stone.py`, bodies unchanged:** the set-out and laying helpers (`flights_of` to `step_plan`, `widths`, `settler`, `top_*`, `seat_dab`, `make`, `slug`). Their literals now come from `configure`.
- **New in `stone.py`:**
  - `configure` and `defaults`: the rules from the kind, `stairs.json`, the materials and `pack.json`;
  - `spec_of`, `way_id`, `lane_of`;
  - `FLIGHTS` from the record;
  - `info_of`, `make_all`, `write_export`.
- **Wrappers:** `lay` and `compose` now wrap `stair_stages.compose`; `build` adds the sidecar.
- **`lay`'s 510 lines went to `stair_stages.py`:**
  - `plan_stair`: the set-out, widths, wet and rise-error draws;
  - `life_stair`: campaigns, and per flight the resets, settling, mortar, slabs and cracks;
  - `geometry_stair`: `put`'s first half, the fills, joints and rows;
  - `bake_stair`: `put`'s second half (polish to UV3);
  - `meshes_of`, `sidecar`, and the seven stage entries.
- **`setout_check.py`:** its imports are lazy, and it reads patience from the keeper.

## For 2b
- `legacySeed` 1. House runs now default to the pack's 1989.
- Facts read the way from `heart_layout.py` in floats, so plan and life carry floats: 1,134 and 675 floats counted by checks.
- The facts output adds `townPlan`, so it no longer equals the record's hash.
- Inline literals:
  - `flights_of`'s 0.65 and 0.09;
  - the slab finish ranges;
  - the crack gap, settling, sett sizes and kerb ranges.
- Pointing fills are always 0.
- Landing slab streams are keyed on the slot, tread slabs on the fill.
- Upkeep's keeper word is "town".
- A record holds a single period of use.
- `stairs.json` has no schema.
- The levels and budget are provisional.
- **The upkeep decade fix:** moving the date to 1990 changes past events (a crack's year, a corner's filling year), so history is not a stable prefix.
- The eight `--` ids, the wall-head slots, renaming the seed keys, and integer-mm plans.
- The repo's variety JSONs lack the new keys until they are rebuilt.

## Decisions where the plan left room
- Campaigns are drawn in life, keyed by work index.
- The sidecar:
  - coordinates are in the mesh frame, at 3 decimals;
  - affordances run `from` the year built `to` null;
  - the walk affordance carries the walking breakline;
  - collision is `none` per mesh, with `proxy: affordances` and the walkable ids.
- The geometry and bake goldens are blob refs plus per-piece and per-chunk summaries: 432 and 243 KB.
- Each stage sets only its own rules through `ST.configure`, from its params and tables. Geometry reads only its own and the materials.
- The stair test swaps `lane_of` for the golden facts' path, which skips the 70 s import.

## Against the schemas
- A record edit reruns everything, because facts hash the record file. `hashing.md` says content-addressed.
- A changed input changes its stage's link even when the output is the same, so the stages after it rerun.
- `record.where.at` is unused: the origin comes from the town plan.

## Incident
- My Blender runs overlapped R2c's player at 08:45:10–26 and 08:46:10–33. At 08:44, Unity had not started yet.
- I reported it at once, and R2c reran.
- My first wait loop matched its own command line. It now waits on R2c's pid file and anchored process names.
