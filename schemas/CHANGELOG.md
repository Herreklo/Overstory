# Contracts changelog

Every change to the files in `schemas/` with its migration. The contracts' version is `schemaVersion`, carried by every record, kind, pack file and fixture. `tools/migrate.py` runs `migrations/NNN_<name>.py` in order on every file behind; `tools/migrate.py --check` fails while any is behind. `tools/validate_record.py` checks records, kinds, parts and the registries against the current version.

## 2, unchanged: the walling table's schema (23 October, the gully port's step 2b, R1)

No migration: the pack's one walling table already had this shape, and no record or kind changes.

New:
- `walling.schema.json`: a pack's walling table (`packs/<pack>/walling.json`, the wall kind's table `walling`), by working: a wall's working (every course, stone, coping, topstone, head and through number, required together), a rebuilt panel's (its edge stones) or a stair's (its steps' laps and joints), each naming its material, integers in millimetres. Only a test table names the workings it `applies` (design.md 7b). `tools/validate_record.py` validates every pack's `walling.json` and the test tables merged into it (`reviews/lt1/port/2b/r1/granite-1930.json`, whose provenance is now `authored`), and checks what the schema cannot say: each range's least no more than its most, each drawn length's fractions in order, each working's material one of the pack's, and a test table's workings not the pack's own. `stairs.json` still has no schema.

## 2, unchanged: history as a function (22 October, the gully port's step 3)

No migration: no record, kind or part holds intervals or pages yet, and every addition is optional. Decisions D5.1, D5.4 and S2 amended, D5.10 new.

Changed:
- `maps.json`: p0 holds feet (R) and static water (G); h1 holds polish's amplitude, lichen's rate, moss's damp and the bed reach, baked on each piece as laid and rebuilt on geometry, a rate or a reach. New `charts` (per run of one face kind, a 16-texel grid, 2 texels of padding, 3 mips, trilinear), `pageFormat` (BC7 per page from the real page's error at R3's end, 99th percentile at most 2/255; a failing pair goes BC5; no grain in pages) and `bakers` (one bake function, golden page hashes; step 3 bakes offline until step 5). New unknowns: page format and chart shimmer.
- `layers.json`: a `law` per fitted layer (amplitude or rate, its clock, curve and delay); moss's `scale`, `careFactor` and `order` (clip, then the trodden thinning); the hollow as a `derived` layer, with no channel; `readers` per family (the stone reads p0 and h1). h1.a is the bed reach.
- `interval.schema.json`: the description says how an interval drives the law; an optional `reach` (a lift by hands or a relaid bed, its date the piece's disturbed clock); the age brought is whole years.
- `chunk-format.md` §4: the piece table is 32 bytes with four named resets (placed, disturbed, cleaned, reserved) as year × 16 + month, the age brought in whole years and the inherited polish; its GPU entry is 16 bytes.
- `channels.json`: uv1's bare year and variation are the piece table's; uv3 carries the hands' reach; uv4.y (the hollow rate) is reserved and walked stone writes 0; stone writes no uv5.

## 2, unchanged: the stair as a kind (22 October, the gully port's step 2a)

No migration: every addition is optional, and no record, kind or part needs rewriting.

New:
- `material.schema.json`: a pack's material (`packs/<pack>/materials/<material>.json`, the stages' table `materials`), minimal for now: how deep feet wear it (`wearUmPerCentury`) and how readily it cracks (`cracksPerMille`). `packs/stavanger-1989/materials/slate.json` and `granite.json` hold the values `stone.py` held.
- `record.schema.json`: an optional `use`, a record's periods of use, each from a date with its `footfall` a year (the stair's footfall, which `stone.py` held as a constant). `tools/validate_record.py` checks that the first period starts with the lifespan, the periods run in order, a period's event is at its date and a derived period names its rule. It also validates every pack's materials against `material.schema.json` and checks each file's name is its material.
- `kinds/stair.json`, the stair kind, live through `blender/generators/stair_stages.py`. Its plan rules are in its params, in millimetres and per mille.
- `fixtures/records/st-gully.json`, the gully steps as a record.
- `packs/stavanger-1989/stairs.json`, the builders' patience and the codes' limits. It is read as the table `stairs`; no schema validates it yet.
- `packs/stavanger-1989/pack.json`: `worldSeed` 1989, the run's seed when no `--world-seed` is given. The stair's stages key their draws on `legacySeed` 1 until step 2b's re-baseline.

## 2, unchanged: the grammar holds step 0b's seed keys (22 October)

No migration: no key in code changed, so step 0b's proposed baseline stands. `naming.md` gains `stair-flaw-part` (a crack's pointing and front, `<slab fill>/ck/pt`, `/ck/front`) and `wall-hearting` (`<place>/ht-<m>`), and says how a seed key is made: an id, then purpose words and integers. The setts as pieces of their row's fill and the wall's `sp-` places, pending below, landed in step 0b. Left for step 2b's re-baseline: the wall's heads, keyed on their course with `"head"`, take slots; the eight stair ids that slug a lane's name to `--` are minted afresh.

## 2, unchanged: the hash chain and the stage contract (22 October, the gully port's step 2 groundwork)

No migration: no field changed, and no record, kind or part needs rewriting.

New:
- `hashing.md`: the canonical encoding a C# twin reproduces (sorted keys, integers as decimal text, floats by their binary64 bits, strings as UTF-8), the blob hash for bulk numbers and the chain's links and cache keys. `tools/hashes.py` implements it; its vectors are `fixtures/golden/canon-vectors.json`.
- `stages.md`: the stage contract, run by `tools/run_kind.py`. It covers the entry and its context, outputs, the cache, stage files, the golden fixtures in `fixtures/golden/<kind>/<stage>.json` and `tools/diff_stage.py`.

Changed:
- `kind.schema.json`: a stage's `reads` also admits the run's input `date`, besides the pack's tables. Only the description changed.
- `kinds/house.json`: facts is live through the shared `tools/stages/record.py:facts`. Checks moves from `tools/validate_record.py:validate`, whose signature never fit a stage, to `tools/stages/record.py:checks`.

## 2: the contracts as files (22 October, the gully port's step 1)

Migration: `migrations/001_schema_2.py`. The provenance word `engine` is retired for `simulated`; every file's `schemaVersion` goes from 1 to 2. Today's bundles (`fixtures/lt1-corner.json`, `lt1-street.json`, `lt1-town.json`) held no `engine`, so only their version changed. They stay bundles; each kind's port turns its part of them into records, with that port's migration.

New:
- `naming.md`, the grammar every id and name follows, read by `tools/naming.py`, which writes each schema's patterns.
- `record.schema.json`, `slot.schema.json`, `interval.schema.json`, `kind.schema.json`, `part.schema.json`, `plan.schema.json`, `world-state.schema.json`, `change-query.schema.json`, `chunk.schema.json`.
- `channels.json`, `maps.json` (with the face classes, the texel rule, each map's format and encoder, the shell bake's input and the four unknowns), `layers.json`.
- `chunk-format.md`, the container and its units, reserved: no writer or reader until step 5.
- `kinds/house.json` and `fixtures/records/bld-104.json`: a second kind on paper, validated and not built. `packs/stavanger-1989/` with its years (`pack.json`), its tools (`tooling.json`) and the five draft parts house 104 uses.

Pending, for step 2's re-baseline: `stone.py` keys a sett row's setts as `<row>/<c>` and `wall.py` a wall course's stones as `<course>/<j>`. By the grammar a bare count after a slot is a fill, so these become `<row>/0#<c>` (the setts as pieces of the row's fill) and `<course>/sp-<j>`. Both re-seed only what they name; step 2 keeps the generators' keys until its deliberate re-baseline, and that step's migration renames them in any record that holds them.

Also pending: `blender/tools/corner_fixture.py` and `grow_town.py` still write `schemaVersion` 1. A bundle written again comes out behind, `migrate.py --check` fails on it, and `migrate.py` brings it up. The writers move to 2 when next changed.
