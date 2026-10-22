# Step 2a: how stone.py splits into the stair's seven stages (draft)

Written 22 October by the step 2 groundwork agent, before 0b's go. It was read against `stone.py` as 0b left it at about 03:40, while 0b was still editing it: names are given, line numbers are not. It rests on the groundwork's contract (`schemas/stages.md`, `schemas/hashing.md`), which is the runner's, and on the rule that rules 2a: **the gully's FBX, and the cheek walls', hash exactly what 0b's baseline hashes.**

## The one idea that makes it safe

Every draw comes from a stream keyed on (world seed, a stable id, a purpose). Streams are independent, so a draw can move to another stage, or happen earlier or later, without changing a value, provided **each stream's own draws stay in the same order**. Float arithmetic must also stay in the same order: same expressions, same operands, float64 throughout. JSON round-trips Python floats exactly, so plan and life can hand floats across the cache in 2a. The split therefore assigns **whole streams** to stages. It never splits one stream's draws between two stages.

Integer params need care. `integerStage` forbids floats in the params of facts, plan and life, so a rule constant is written in integer mm or per mille, and the code divides by `1000.0`. Division is correctly rounded, so `300 / 1000.0` is the very double `0.3` parses to. Every constant in `stone.py` has at most three decimals, so this is bit-exact. Geometry and bake params may stay floats.

## Function to stage

| Today | Stage | Notes |
| --- | --- | --- |
| `FLIGHTS["gully"]`, `YEAR` | facts (the record), the run's `date` | `fixtures/records/st-gully.json`; `YEAR` becomes `ctx.date` (1989 = the pack's showYear) |
| `STONES` | pack `materials/slate.json`, `granite.json` | read by life (cracks), geometry (wear) and bake (wear) as `table:materials` |
| `flights_of(lane)`, the `heart_layout` lane lookup | plan | the 2a exception: the lane's float path still comes from `heart_layout`, looked up through the record's `on` link (below); it ends in 2b |
| `stone_rises`, `going_of`, `landing_min`, `practice_limit`, `rests_needed`, `fits`, `_narrow`, `setout_feasible`, `step_plan` | plan | unchanged functions, kept in `stone.py` (wall.py and setout_check.py call them) |
| lean draw, campaign-flight draw, per-tread `widths` (slab edges), `wet` sinks and values, `err` (rise), the step stream (tread thickness, overhang, riser edges; a step-ramp's kerb depth, height and edges) | plan | each a whole stream, none of which reads life |
| `UP.flight`, `UP.keeper_in(.., YEAR-1)` (care_now) | life | `upkeep.py` unchanged; its `busy` needs lean and W from the plan |
| `put` (first half: across, along, foot, worn, nose, P moved; then X, Y, Z, faces and UV0 with the ang, off and var draws), `settler`, `top_line`, `seat_dab`, `fill`, `fill_bed`, `fill_front`, `point`, `pave`, the per-step loop, setts, slabs, cracks, dabs, joints, landings, turn | geometry | every per-piece stream (`lay`, `marks`, `row`, the part seeds `h(id)`, `crack/gap`, `crack/drop`) |
| `put` (second half: polish, lichen, moss, held, water, sky, ground; UV1's `bare_y / 200`) | bake | `step_wet` (`h(tid, "moss")`) moves with it; no streams |
| `make`, the FBX export, the info JSON, `mesh_hash.write_manifest` | export | the only stage that needs `bpy` |
| `setout_check`'s per-flight rules, ids, the hash proof | checks | below |

`put` splits where P has been moved. Its draws (ang, off ×2, var) are the only draws `put` makes, and the piece's stream is fresh or at the same point either way, so they stay in geometry. **Geometry emits, per vertex and in placement order:** the position, `kind`, `edge`, local y (the joint test), `across`, `along`, z placed (`z0 + P.z`) and `worn`. **Per piece** it emits foot_on, worn_y, bare_y, bed_y, lifted_y, polish0, the step's index, the destination mesh (main or setts) and var. **Per step:** zfoot, z_top, cur S and D, h and g. **Per flight:** W, lean, trod and care_now. Bake recomputes `foot` and `walking(...)` from the same arrays with the same expressions. Vertex order is the FBX's order, so geometry and bake must both keep `put`'s call order. Faces have mixed sizes, so they go out as two blobs: the corner indices and the face sizes.

## What each stage outputs

- **facts:** the record, validated (shared entry `tools/stages/record.py:facts`). Its output hash is the record hash. It must stay the record, so the lane's path is not added here: plan reads it.
- **plan** (no `date`; it reads the record, its params and `stairs.json`, and the town plan, which enters its key through the code fingerprint as an imported module):
  - per stair: `lean`, the campaign flight per event id, `origin`, `flags`;
  - per flight `fl-<n>`: a, b, W, flag or `{n, r, g, S, D, start, rests, limit, cuts, landings, fallback}`, its `wet` per step;
  - per step `tr-<i>`: the slab slots `sl-<k>` with their edges, the riser slots `rs-<k>` and kerb slots `kb-<k>` with theirs, the joints `jt-<k>`, the tread thickness, overhang, kerb depth and height, and `err`.
  - Floats in 2a (the shared check counts them); integer mm in 2b.
- **life** (reads `date`, `materials`):
  - per flight: `care_now`;
  - per step: `reset`, `settled`, `mortar`;
  - per slab slot: its current fill id (`<slot>/<n>`), origin, placed, lifted, bare, shim, and `cracked` and `corner` with their year, place and filling.
  - The info JSON's `life` list is derived from this in export, so it keeps its `off_mm` rounding.
- **geometry** (reads `date`, `materials`): per mesh (`stone_gully_<fi>` and `_setts`), blobs for V, the face loops and sizes, UV0 and the bake inputs above. Per piece: `{fill, chunk, hash, verts, faces}`, then `hashes.summarise_pieces`.
- **bake** (reads `date`, `materials`, `bakeVersion`): per mesh, blobs COL (n×4), UV1, UV2 and UV3, with per-piece summaries.
- **export** (`bpy`): writes `unity/Assets/Art/Stone/stone_gully.fbx`, its `.json` and `mesh-hashes.json` (each named with `ctx.wrote`). It outputs mesh_hash's per-mesh, per-channel hashes and the triangle counts.
- **checks:** the shared id and float checks, plus the stair's own:
  - the set-out rules from `setout_check` for this record's flights;
  - every slab slot in plan has exactly one current fill in life;
  - the piece counts agree between geometry and bake.

## Where ids are minted

| Id | Minted by | Today in |
| --- | --- | --- |
| `st-gully` | the record (authored) | `FLIGHTS["gully"]["id"]` |
| `fl-<n>`, `fl-<n>/turn` | plan | `flight_id`, `pave(f"{fid}/turn")` |
| `tr-<i>`, `sl-<k>`, `rs-<k>`, `kb-<k>`, `jt-<k>`, `jt-<k>/front`, `bed`, `ld`, `sets`, `sets/bed` | plan | geometry's loop today; plan already knows every one (edges and form), so plan names them and geometry uses the names |
| `<slab>/<n>` (fills) | life (`upkeep.flight`: 0 as laid, +1 per replacement) | `upkeep.py` |
| `jt-<k>/pt`, `bed/pt` (a pointing exists only once a work pointed it) | life, from the work that pointed it | geometry composes them from life's mortar |
| `<fill>/ck`, `<fill>/dab` | life (the crack or corner event) | geometry composes `f"{key}/dab"` |
| `ld/rw-<r>`, `turn/rw-<r>`, `<row>/sl-<k>`, `sets/rw-<r>` | **geometry in 2a** (a known exception): the row widths are the first draws of the `row` streams that also lay the row's pieces | `pave`, the sett loop |
| pieces `<fill>#<i>`, `<row>/0#<c>` | geometry | as today |

Moving the rows to plan means drawing a row's width in plan and skipping that draw in geometry. That is hash-safe but clumsy, so it waits for 2b, which re-seeds anyway. One more 2b item: a landing slab's stream is keyed on its slot (`<row>/sl-<k>`), where a tread slab's is keyed on its fill (`<slot>/<fill>`).

## Constants: kind or pack

**`kinds/stair.json`** holds the rules of a stair anywhere, in integer mm and per mille (plan, life) or floats (geometry, bake):
- **Stride and set-out:** stride 630, going at least 260, rise at most 200, ramp below 100 ‰ and step-ramp below 180 ‰ of slope, stride at most 700.
- **Slabs and joints:** lap 100 and joint 4 to 12 (geometry).
- **How a step is built (plan):** `tread_on_riser` has tread 60 to 80, overhang 20 to 30 and riser 160 to 240; `block` has a bed of 60. The rise error by finish is dressed 4, split 12 and rough 20.
- **Plan's draws:** the `widths` ranges by finish, the lean range ±800 ‰ and the wet model's coefficients.
- **Geometry and bake:** the shape constants (sunk 0.2, the sett ranges, the joint fills' sizes, the damp, sky and ground values). In 2a these may stay in the code as the part functions' own, recorded as such. They are not facts.

**The pack** holds what is the place's or the era's:
- `materials/slate.json` gives wear 8000 µm a century and cracks 1000 ‰. `granite.json` gives 2000 and 250.
- Builder patience by keeper role (`town` 11 to 16, `society` 10 to 14, owners 8 to 20) is keyed by the pack's keeper words, and **the limits of real practice (18 risers, 3.3 m: DIN 18065, TEK17)** are national codes. I recommend a pack table `stairs.json` read by plan, not the kind. The brief lists only rise, lap, joints, step build and stride for the kind, so this is my call to confirm.
- There is no `material.schema.json`. 2a should add a minimal one (wear, cracks), with a CHANGELOG line, so the tables are validated like the rest.

**The record** (`st-gully.json`) holds the facts, in integers:
- **Lifespan and links:** the built event 1874 with params `{stone, builtAs, finish}`, and `lifespan.madeBy` pointing to it. The link `{rel: "on", id: "way-gully-steps"}` names the lane; plan finds its `heart_layout` lane by name.
- **Keepers:** one keeper, the town, from 1874.
- **Care:** 500 from 1874, 300 from 1930, 450 from 1946 and 250 from 1965, with basis `money`.
- **Works:** the campaigns of 1911 (`share 250`) and 1952 (`share 400, mortar cement, stock reclaimed`) as events.
- **Where:** `where.at` is the lane's foot, rounded to mm. Code does not read it until 2b.

**Footfall has no home in a record** (it is the way's fact, engine request 16, "authored" until habits exist). I recommend a pack table `ways.json` keyed by way id (`way-gully-steps: {footfall: 50000}`), read by life, geometry and bake. The record schema stays unchanged.

**The world seed:** the stair's baseline is built with seed 1 and the pack has no `worldSeed`. Add `"worldSeed": 1` to `pack.json` (or always pass `--world-seed 1`). `heart_layout`'s own seed, 1989, places the lanes. It stays its own until the town is a kind, because changing it moves the lane.

## Keeping the other callers whole

- `wall.py` imports `YEAR, FLIGHTS, slug, flights_of, step_plan, make`. `setout_check.py` imports the set-out functions, `VARIETY`, `RUN_*` and `FLIGHTS`. `stair_variety.py` imports `make, lay, flights_of`.
- `stone.py` therefore stays the library. The stage bodies are written as plain functions (spec-like inputs, no `ctx`) in `blender/generators/stair_stages.py`, with thin `ctx` entries named in `kinds/stair.json`.
- `lay(spec, seed)` stays as their composition, so the variety sheet keeps working.
- `FLIGHTS` becomes `{"gully": spec_of(record)}`, read from `st-gully.json`. `YEAR` stays as the pack's showYear for the wall until the wall is split.
- The constants keep their names in `stone.py`, read from the kind and pack files once at import, so `setout_check` and `wall.py` need no edit. The wall's hash then proves that the shared set-out did not move.

## The proof, in order

1. **Before any edit:** build the gully and the cheek walls as 0b left them, and copy `mesh-hashes.json` aside as the target.
2. **Split in small moves**, rebuilding and running `mesh_hash.py check` against the target after each:
   - record and pack first;
   - then plan out of `lay`;
   - then life;
   - then the `put` split;
   - then export.
   Any difference names the mesh and channel. Diff the plan and life outputs with `tools/diff_stage.py` between a run before a move and one after it.
3. **Run the whole stair twice** through `tools/run_kind.py` in `Blender -b`, with world seed 1 and date 1989. Both FBXs must hash the target, and the second run must skip every stage. Build `wall.py` too; it must hash the target.
4. **Write the goldens:** `fixtures/golden/stair/<stage>.json` with `--golden`. Then `tools/golden.sh` for the golden views (Unity: `pgrep -fl Unity` first).

## Risks

- **0b is still editing `stone.py`** (03:40). Re-read it at the go before cutting.
- **Hidden order:** `widths` and the set-out loops draw a variable number of values. Moving one must move the whole loop, and the move must happen at the same place in that stream's sequence.
- **Float expressions:** writing `a * b * c` as `a * (b * c)`, or a numpy reduction where there was a Python sum, moves bits. Copy the expressions; never "tidy" them in 2a.
- **numpy dtypes:** `kind` is int8 and `edge` float64; geometry's blobs must keep the dtypes `make` reads, or the `float32` cast in `make` is all that hides a change.
- **Cost:** the per-vertex bake inputs add perhaps 10 float64 columns per vertex in the cache. The gully is small, but note it for the town. Step 3 replaces most of them with maps.
- **The info JSON** (`stone_gully.json`) is read by Unity and tools. Export must write it as today, key for key.
